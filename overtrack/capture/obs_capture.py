import ctypes
import ctypes.wintypes
from typing import NamedTuple, Tuple

import cv2
import logging
import os
import psutil
import struct
import time
import hashlib
import numpy as np

from overtrack.game import Frame

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

OpenProcess = ctypes.windll.kernel32.OpenProcess
OpenProcess.argtypes = (ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.wintypes.DWORD)
OpenProcess.restype = ctypes.wintypes.HANDLE

CloseHandle = ctypes.windll.kernel32.CloseHandle
CloseHandle.argtypes = (ctypes.wintypes.HANDLE,)
CloseHandle.restype = ctypes.wintypes.BOOL

# VirtualProtectEx = ctypes.windll.kernel32.VirtualProtectEx
# VirtualProtectEx.argtypes = (ctypes.wintypes.HANDLE, ctypes.wintypes.LPVOID, ctypes.c_size_t, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.DWORD))
# VirtualProtectEx.restype = ctypes.wintypes.LPVOID

ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = (ctypes.wintypes.HANDLE, ctypes.wintypes.LPCVOID, ctypes.wintypes.LPVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t))
ReadProcessMemory.restype = ctypes.wintypes.BOOL

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
# PROCESS_VM_WRITE = 0x0020
# PROCESS_VM_OPERATION = 0x0008
# PROCESS_SUSPEND_RESUME = 0x0800

PyMemoryView_FromMemory = ctypes.pythonapi.PyMemoryView_FromMemory
PyMemoryView_FromMemory.restype = ctypes.py_object
PyMemoryView_FromMemory.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
PyBUF_READ = 0x100


class SHTexDLL:

    @property
    def width(self):
        return self._dll.get_width()

    @property
    def height(self):
        return self._dll.get_height()

    @property
    def pitch(self):
        return self._dll.get_pitch()

    def __init__(self):
        self._dll = ctypes.WinDLL(os.path.join(os.path.dirname(__file__), 'data', 'SHTexCapture.dll'))

        self._dll.init.argtypes = (ctypes.c_ulong,)
        self._dll.init.restype = ctypes.c_void_p
        self.init = self._dll.init

        self._dll.get_width.argtypes = ()
        self._dll.get_width.restype = ctypes.c_ulong
        self._dll.get_height.argtypes = ()
        self._dll.get_height.restype = ctypes.c_ulong
        self._dll.get_pitch.argtypes = ()
        self._dll.get_pitch.restype = ctypes.c_ulong

        self._dll.capture.argtypes = ()
        self._dll.capture.restype = ctypes.c_bool
        self.capture = self._dll.capture

        self._dll.deinit.argtypes = ()
        self._dll.deinit.restype = ctypes.c_int
        self.deinit = self._dll.deinit

        self._last_shtex_handle = None
        self._imageview = None

    def read_texture(self, shtex_handle, colour_mode=cv2.COLOR_RGBA2BGR):
        if self._last_shtex_handle != shtex_handle:
            logger.info('Opening new shtex')
            self._last_shtex_handle = shtex_handle
            self.deinit()
            data_pointer = self.init(shtex_handle)
            if not data_pointer:
                raise ValueError('Failed to init SHTexCapture')

            d11buf = PyMemoryView_FromMemory(data_pointer, self.pitch * self.height, PyBUF_READ)
            img = np.ndarray((self.height, self.pitch), np.uint8, d11buf, order='C')
            img = img[:, :self.width * 4]
            self._imageview = img.reshape((self.height, self.width, 4))

        if not self.capture():
            self._imageview = None
            raise ValueError('Failed capture()')
        return cv2.cvtColor(self._imageview.copy(), colour_mode)


shtex_dll = SHTexDLL()
log_callback = ctypes.CFUNCTYPE(None, ctypes.c_char_p)
shtex_dll._dll.add_log_callback.argtypes = (log_callback,)
shtex_dll._dll.add_log_callback.restype = None


def dll_log(s):
    logger.info(s.decode('ascii')[:-1])


@log_callback
def _dll_log(s):
    dll_log(s)


shtex_dll._dll.add_log_callback(_dll_log)


class CouldNotFindOBSProcess(ValueError):
    pass


class NoOverwatchGameCaptures(ValueError):
    pass


class UnsupportedOBSVersion(ValueError):
    pass


def _get_obs_process(names=('obs64.exe', 'streamlabs obs.exe', 'obs32.exe')):
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if proc.name().lower() in names:
                if proc.parent() and proc.parent().name().lower() in names:
                    return proc.parent().pid
                return proc.pid
        except psutil.NoSuchProcess:
            pass
    return None


try:
    EnumProcessModulesProc = ctypes.windll.psapi.EnumProcessModules
except AttributeError:
    EnumProcessModulesProc = ctypes.windll.kernel32.EnumProcessModules
EnumProcessModulesProc.argtypes = (ctypes.wintypes.HANDLE, ctypes.POINTER(ctypes.wintypes.HMODULE), ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong))
EnumProcessModulesProc.restype = ctypes.c_bool

try:
    GetModuleFileNameExW = ctypes.windll.psapi.GetModuleFileNameExW
except AttributeError:
    GetModuleFileNameExW = ctypes.windll.kernel32.GetModuleFileNameExW
GetModuleFileNameExW.argtypes = (ctypes.wintypes.HANDLE, ctypes.wintypes.HMODULE, ctypes.wintypes.LPWSTR, ctypes.wintypes.DWORD)
GetModuleFileNameExW.restype = ctypes.wintypes.DWORD


def _get_module_base(pid, process_handle, modulename):
    modules = (ctypes.c_void_p * 1024)()
    cbNeeded = ctypes.c_ulong()
    if not EnumProcessModulesProc(process_handle, modules, ctypes.sizeof(modules), ctypes.byref(cbNeeded)):
        raise ValueError('EnumProcessModulesProc failed')
    modules_seen = []
    for module_handle in modules:
        if not module_handle:
            break
        path = ctypes.create_unicode_buffer(512)
        GetModuleFileNameExW(process_handle, module_handle, path, 512)
        basename = os.path.basename(path.value)
        modules_seen.append(path.value)
        if basename == modulename:
            logger.debug('Found base address of %s (%s): 0x%016x', modulename, path.value, module_handle)
            return module_handle, path.value
    logger.error('Failed to find module %s in %d, found %s. Using psutil.memory_maps method', modulename, pid, modules_seen)

    p = psutil.Process(pid)
    logger.debug('Reading memory maps for %s', p)
    maps = p.memory_maps(grouped=False)
    matching_maps = [m for m in maps if os.path.basename(m.path).lower() == modulename]
    logger.debug('Found %d maps: %s', len(matching_maps), ['%s: perms=%s' % (m.addr, m.perms) for m in matching_maps])
    address, path = sorted([(int(m.addr[2:], 16), m.path) for m in matching_maps])[0]
    logger.debug('Found base address of %s (%s): 0x%016x', modulename, path, address)
    return address, path


def _read_ptr(process_handle, address):
    bytes_read = ctypes.c_ulonglong()
    ptr_data = ctypes.c_void_p()
    if not ReadProcessMemory(
            process_handle,
            address,
            ctypes.byref(ptr_data),
            ctypes.sizeof(ptr_data),
            ctypes.byref(bytes_read)
    ):
        raise ValueError('ReadProcessMemory(0x%016x, %d): failed' % (address, ctypes.sizeof(ptr_data)))
    if bytes_read.value != ctypes.sizeof(ptr_data):
        raise ValueError('ReadProcessMemory: expected %d bytes but got %d', ctypes.sizeof(ptr_data), bytes_read.value)
    return ptr_data.value or 0


def _read_str(process_handle, address, length, decode='utf-8'):
    bytes_read = ctypes.c_ulonglong()
    cstr = ctypes.create_string_buffer(length)
    if not ReadProcessMemory(
            process_handle,
            address,
            ctypes.byref(cstr),
            ctypes.sizeof(cstr),
            ctypes.byref(bytes_read)
    ):
        raise ValueError('ReadProcessMemory(0x%016x, %d): failed' % (address, ctypes.sizeof(cstr)))
    if bytes_read.value != ctypes.sizeof(cstr):
        raise ValueError('ReadProcessMemory: expected %d bytes but got %d', ctypes.sizeof(cstr), bytes_read.value)
    if not decode:
        return cstr.raw
    else:
        return cstr.value.decode(decode)


def _read_struct(process_handle, address, fmt):
    length = struct.calcsize(fmt)
    bytes_read = ctypes.c_ulonglong()
    buf = ctypes.create_string_buffer(length)
    if not ReadProcessMemory(
            process_handle,
            address,
            ctypes.byref(buf),
            ctypes.sizeof(buf),
            ctypes.byref(bytes_read)
    ):
        raise ValueError('ReadProcessMemory(0x%016x, %d): failed' % (address, ctypes.sizeof(buf)))
    if bytes_read.value != ctypes.sizeof(buf):
        raise ValueError('ReadProcessMemory: expected %d bytes but got %d', ctypes.sizeof(buf), bytes_read.value)
    return struct.unpack(fmt, buf.raw)


def _read_dstr(process_handle, address):
    ptr, length, capacity = _read_struct(process_handle, address, '@PQQ')
    return _read_str(process_handle, ptr, length)


def _get_dll_hash(pid, path, _module_hash_cache={}):
    key = (pid, path)
    if key not in _module_hash_cache:
        hash_md5 = hashlib.md5()
        with open(path, 'rb') as f:
            hash_md5.update(f.read())
        _module_hash_cache[key] = hash_md5.hexdigest()
        logger.info('obs.dll %s hash is %s', path, _module_hash_cache[(pid, path)])
    return _module_hash_cache[(pid, path)]


def open_obs():
    pid = _get_obs_process()
    if not pid:
        logger.error('Could not find OBS process')
        return None, None

    logger.info('Found OBS process %d', pid)

    process_handle = OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    logger.info('Opened process')

    return pid, process_handle


def close_obs(process_handle):
    CloseHandle(process_handle)


OBS_OFFSETS = {
    # Find OBSDLL_OBS_OFFSET by looking for `obs`
    # If this symbol is hard to find bp some function that uses it straight away e.g. obs_hotkey_inject_event

    # 00007FF9F3CA4F00 | 40 53                              | push rbx                                              |
    # 00007FF9F3CA4F02 | 41 56                              | push r14                                              |
    # 00007FF9F3CA4F04 | 48 83 EC 48                        | sub rsp,48                                            |
    # 00007FF9F3CA4F08 | 48 8B D9                           | mov rbx,rcx                                           |
    # 00007FF9F3CA4F0B | 48 89 4C 24 38                     | mov qword ptr ss:[rsp+38],rcx                         |
    # 00007FF9F3CA4F10 | 48 8B 0D 81 71 05 00               | mov rcx,qword ptr ds:[7FF9F3CFC098]                   | <-- absolute address is 0x7FF9F3CFC098
    # 00007FF9F3CA4F17 | 44 0F B6 F2                        | movzx r14d,dl                                         |

    'default': {
        'OBS_FIRSTSOURCE_OFFSET': 0x3f0,

        'SOURCE_NAME_OFFSET': 0x0,
        'SOURCE_DATA_OFFSET': 0x8,
        'SOURCE_NEXT_OFFSET': 0x90,
        'SOURCE_TYPE_OFFSET': 0xA8,

        'GAMECAPTURE_CX_OFFSET': 0x58,
        'GAMECAPTURE_TITLE_OFFSET': 0x100,
        'GAMECAPTURE_SHOWING_OFFSET': 0xEF,
        'GAMECAPTURE_CONFIG_OFFSET': 0x100,
        'GAMECAPTURE_DATA_OFFSET': 0x208,

        'CAPTURE_CONFIG_CURSOR_OFFSET': 0x28
    },

    '1428ce43ee3e9585d07f953f332bcbf6': {
        'name': 'OBS 20.1.3',

        'OBSDLL_OBS_OFFSET': 0xd3820,
    },

    '5d7a88d4ca4671676c4051800fe37cd6': {
        'name': 'OBS 21.0.1',

        'OBSDLL_OBS_OFFSET': 0xD5820,
    },

    '76cbcdb0011ddf8e3209fd11750ca4c0': {
        'name': 'Streamlabs 0.8.4',

        'OBSDLL_OBS_OFFSET': 0xbc098,
    },

    '156e00b4eaf9d57358c9faca62f47a79': {
        'name': 'Streamlabs 0.8.7',

        'OBSDLL_OBS_OFFSET': 0xbc098,
    },

    'af1e7b671c5d8cd884cab8d1497e8622': {
        'name': 'Streamlabs 0.8.10',

        # 00007FFE90FB61B0 | 48 8B 0D E1 6E 05 00               | mov rcx,qword ptr ds:[7FFE9100D098]                   |
        'OBSDLL_OBS_OFFSET': 0xbd098,
    },

    '8da8be61f6f590275d0b3c7bb9b95e77': {
        'name': 'OBS 21.1.0',

        'OBSDLL_OBS_OFFSET': 0xc8858
    },

    'dc11172396cfc105070cd0f378973bc5': {
        'name': 'Streamlabs 0.8.16',

        # 00007FFC327A61B0 | 48 8B 0D E1 6E 05 00               | mov rcx,qword ptr ds:[7FFC327FD098]                   |
        'OBSDLL_OBS_OFFSET': 0xbd098
    },

    '157349dfe3ae53f1d18b41b591ebda47': {
        'name': 'OBS 21.0.2',

        # obs.dll+6B0B0 - 48 8B 0D A1C70500     - mov rcx,[obs.obs] { [1ADCF818000] }
        # obs.dll+6B0B0 - 48 8B 0D A1C70500     - mov rcx,[obs.dll+C7858] { [1ADCF818000] }
        'OBSDLL_OBS_OFFSET': 0xC7858
    },

    '952781e377263fd02b95f4de4f902c50': {
        'name': 'Streamlabs 0.9.2',

        # 00007FF8331B6300 | 48 8B 0D 81 6D 05 00     | mov rcx,qword ptr ds:[7FF83320D088]     |
        # ...
        # Found base address of obs.dll (...\obs.dll): 0x00007ff833150000
        # >>> hex(0x7FF83320D088 - 0x00007ff833150000)
        # '0xbd088'

        'OBSDLL_OBS_OFFSET': 0xbd088
    },

    '07176f21fd4ad971eb61625704ce5e70': {
        'name': 'Streamlabs 0.9.3',
        'OBSDLL_OBS_OFFSET': (0x7ffd7821d088 - (0x00007ffd78161000 - 0x1000))
    },

    '58e3231e5000d11d16978dfad3b63519': {
        'name': 'OBS 22.0.1',
        'OBSDLL_OBS_OFFSET': 0xcc828
    },

    '39f19623b8bc1f9769af4fb5f2fdb052': {
        'name': 'OBS 22.0.2',
        'OBSDLL_OBS_OFFSET': 0xcc828
    }

}


# def get_sources(pid, process_handle, _module_base_cache={}, _patched_processes=set()):
def get_sources(pid, process_handle, _module_base_cache={}):
    if pid in _module_base_cache:
        base, path = _module_base_cache[pid]
    else:
        base, path = _get_module_base(pid, process_handle, 'obs.dll')
        _module_base_cache[pid] = base, path

    hashh = _get_dll_hash(pid, path)
    if hashh not in OBS_OFFSETS:
        raise UnsupportedOBSVersion('Unknown OBS version with hash: %s' % (hashh,))

    offsets = dict(OBS_OFFSETS['default'])  # type: dict{str, int}
    offsets.update(OBS_OFFSETS[hashh])

    obs_struct_ptr_address = base + offsets['OBSDLL_OBS_OFFSET']
    logger.debug('Trying to read OBS struct ptr from 0x%016x', obs_struct_ptr_address)
    obs_struct_address = _read_ptr(process_handle, obs_struct_ptr_address)
    logger.debug('Got obs struct at 0x%016x', obs_struct_ptr_address)
    obs_datafirstsource_ptr_address = obs_struct_address + offsets['OBS_FIRSTSOURCE_OFFSET']
    logger.debug('Trying to read obs->data.first_source from 0x%016x', obs_datafirstsource_ptr_address)
    sources = []
    obs_source_ptr = obs_datafirstsource_ptr_address
    for _ in range(256):
        obs_source = _read_ptr(process_handle, obs_source_ptr)
        logger.debug('Reading source pointer 0x%016x = 0x%016x', obs_source_ptr, obs_source)
        if not obs_source:
            logger.debug('Reached end of source list')
            break
        logger.debug('Got source = 0x%016x', obs_source)

        obs_source_name_ptr = _read_ptr(process_handle, obs_source + offsets['SOURCE_NAME_OFFSET'])
        obs_source_name = _read_str(process_handle, obs_source_name_ptr, 64)
        logger.debug('Got source->name = 0x%016x = %s', obs_source_name_ptr, obs_source_name)

        obs_source_type_ptr = _read_ptr(process_handle, obs_source + offsets['SOURCE_TYPE_OFFSET'])
        obs_source_type = _read_str(process_handle, obs_source_type_ptr, 64)
        logger.debug('Got source->type = 0x%016x = %s', obs_source_name_ptr, obs_source_type)

        sources.append((obs_source_name, obs_source_type, obs_source, offsets))

        obs_source_ptr = obs_source + offsets['SOURCE_NEXT_OFFSET']
        logger.debug('Got source->next = *0x%016x', obs_source_ptr)
    return sources


class OBSGameCapture:

    def __init__(self, process_handle, addr, offsets, name=None, colour_mode=cv2.COLOR_RGBA2BGR):
        self.name = name
        self.process_handle = process_handle
        self.addr = addr
        self.offsets = offsets
        self.colour_mode = colour_mode
        self._read()
        self._last_shtex_handle = None
        logger.debug('Got 0x%016x = %s', addr, self)

    def __repr__(self):
        optstr = ''
        if self.name:
            optstr = 'name=%s, ' % (self.name,)
        return 'OBSGameCapture(%stitle=%s, cx=%s, cy=%s, pitch=%s, showing=%s, active=%s, capturing=%s, force_shmem=%s)' % (
            optstr, self.title, self.cx, self.cy, self.pitch, self.showing, self.active, self.capturing, self.force_shmem
        )

    def __hash__(self):
        return hash(tuple(list(enumerate([
            self.title, self.cx, self.cy, self.pitch, self.cursor, self.force_shmem,
            self.force_scaling, self.allow_transparency, self.limit_framerate,
            self.capture_overlays, self.anticheat_hook, self.shmem_data,
            self.texture_buffer_0, self.texture_buffer_1
        ]))))

    def _read(self):
        self.cx, self.cy, self.pitch = _read_struct(self.process_handle, self.addr + self.offsets['GAMECAPTURE_CX_OFFSET'], '<III')
        self.title_ptr = _read_ptr(self.process_handle, self.addr + self.offsets['GAMECAPTURE_TITLE_OFFSET'])
        if not self.title_ptr:
            self.title = None
        else:
            self.title = _read_str(self.process_handle, self.title_ptr, 64)
        self.showing, self.active, self.capturing = _read_struct(
            self.process_handle,
            self.addr + self.offsets['GAMECAPTURE_SHOWING_OFFSET'],
            'B' * 3
        )
        self.cursor, self.force_shmem, self.force_scaling, self.allow_transparency, \
        self.limit_framerate, self.capture_overlays, self.anticheat_hook = _read_struct(
            self.process_handle,
            self.addr + self.offsets['GAMECAPTURE_CONFIG_OFFSET'] + self.offsets['CAPTURE_CONFIG_CURSOR_OFFSET'],
            'B' * 7
        )
        self.shmem_data, self.texture_buffer_0, self.texture_buffer_1, self.copy_texture_func = _read_struct(
            self.process_handle,
            self.addr + self.offsets['GAMECAPTURE_DATA_OFFSET'],
            '@PPPP'
        )

    def read_texture(self, reread=True):
        if reread:
            self._read()
        if not self.showing or not self.active or not self.capturing:
            logger.debug('%s must have showing=1, active=1, capturing=1', self)
            return None
        if self.force_shmem:
            if not self.copy_texture_func:
                logger.warning('%s copy_texture_func was NULL but force_shmem=%d', self, self.force_shmem)
                # return None

            size = self.pitch * self.cy
            imb = ctypes.create_string_buffer(size)
            bytes_read = ctypes.c_ulonglong()
            if not ReadProcessMemory(
                    self.process_handle,
                    self.texture_buffer_0,
                    ctypes.byref(imb),
                    size,
                    ctypes.byref(bytes_read)
            ):
                raise ValueError('ReadProcessMemory(0x%016x, %d): failed' % (self.texture_buffer_0, ctypes.sizeof(imb)))
            if bytes_read.value != ctypes.sizeof(imb):
                raise ValueError('ReadProcessMemory: expected %d bytes but got %d', ctypes.sizeof(imb), bytes_read.value)

            data = np.frombuffer(imb.raw, dtype=np.uint8).copy()
            data = np.reshape(data, (self.cy, self.pitch))
            data = data[:, :self.cx * 4]
            data = data.reshape((self.cy, self.cx, 4))
            return cv2.cvtColor(data, self.colour_mode)
        else:
            bytes_read = ctypes.c_ulonglong()
            texture_handle = ctypes.c_uint32()
            if not ReadProcessMemory(
                    self.process_handle,
                    self.shmem_data,
                    ctypes.byref(texture_handle),
                    ctypes.sizeof(texture_handle),
                    ctypes.byref(bytes_read)
            ):
                raise ValueError('ReadProcessMemory(0x%016x, %d): failed' % (self.shmem_data, ctypes.sizeof(texture_handle)))
            if bytes_read.value != ctypes.sizeof(texture_handle):
                raise ValueError('ReadProcessMemory: expected %d bytes but got %d', ctypes.sizeof(texture_handle), bytes_read.value)
            if not texture_handle or not texture_handle.value:
                raise ValueError('Got texture_handle=0x0')
            return shtex_dll.read_texture(texture_handle.value, self.colour_mode)


def get_gamecapture_matching(pid, process_handle, title, colour_mode=cv2.COLOR_RGBA2BGR):
    sources = get_sources(pid, process_handle)
    logger.debug('Got sources %s', [s[0] for s in sources])

    game_captures = [
        OBSGameCapture(process_handle, _read_ptr(process_handle, addr + offsets['SOURCE_DATA_OFFSET']), offsets, name=name, colour_mode=colour_mode)
        for (name, typ, addr, offsets)
        in sources
        if typ == 'game_capture'
    ]

    if not len(game_captures):
        return None

    matching_captures = [gc for gc in game_captures if gc.title and gc.title.lower() == title.lower()]
    if not len(matching_captures):
        return None
    elif len(matching_captures) == 1:
        return matching_captures[0]
    else:
        logger.debug('Got %d game captures with title=%s' % (len(matching_captures), title))

        prop_priority = ['capturing', 'active', 'showing']
        for prop in prop_priority:
            best = [c for c in matching_captures if getattr(c, prop) == 1]
            if len(best):
                return best[0]


class OBSFrameExtractor:
    
    class OBSFrameMetadata(NamedTuple):
        game_title: str
        obs_version: str

        force_shmem: bool
        force_scaling: bool
        original_shape: Tuple[int, int]
        cursor: bool

        cx: int
        cy: int
        pitch: int

    def __init__(self, game_title: str, debug=False) -> None:
        self.game_title = game_title
        self.debug = debug
        self.game_capture: OBSGameCapture = None
        
    def get(self) -> Frame:
        if not self.game_capture:
            if not self._capture_game():
                return self._generate_blank_frame()
        try:
            return self._generate_frame()
        except Exception as e:
            logger.exception('Got exception reading frame, attempting to recreate game capture', exc_info=e)
        if self._capture_game():
            try:
                return self._generate_frame()
            except Exception as e:
                logger.exception('Got second exception reading frame following creation of game capture - sending blank frame', exc_info=e)
            self.game_capture = None
            return self._generate_blank_frame()

    def _generate_frame(self) -> Frame:
        image = self.game_capture.read_texture(reread=True)
        if image is None:
            raise ValueError('Image was none')

        original_shape = image.shape
        if image.shape[:2] != (1080, 1920):
            image = cv2.resize(image, (1920, 1080))
        if image.shape[2] == 4:
            alpha, image = image[:, :, 3], image[:, :, :3]
        else:
            alpha = None
        return Frame.create(
            image=image,
            timestamp=time.time(),
            debug=self.debug,

            alpha_image=alpha,

            source=self.OBSFrameMetadata(
                game_title=self.game_title,
                obs_version=self.game_capture.offsets['name'],
                original_shape=original_shape,

                force_shmem=bool(self.game_capture.force_shmem),
                force_scaling=bool(self.game_capture.force_scaling),
                cursor=bool(self.game_capture.cursor),
                cx=self.game_capture.cx,
                cy=self.game_capture.cy,
                pitch=self.game_capture.pitch
            ),
        )

    def _generate_blank_frame(self) -> Frame:
        return Frame.create(
            image=np.zeros((1080, 1920, 3), dtype=np.uint8),
            timestamp=time.time(),
            debug=self.debug,
            
            blank_frame=True            
        )

    def _capture_game(self) -> bool:
        # TODO: error handling
        pid, process_handle = open_obs()
        self.game_capture = get_gamecapture_matching(pid, process_handle, self.game_title, colour_mode=cv2.COLOR_RGBA2BGRA)
        return True


def main():
    cap = OBSFrameExtractor('Overwatch', debug=True)
    while True:
        frame = cap.get()
        print(frame)
        im = frame.image
        im = cv2.resize(im, (1440, 810))
        cv2.imshow('overwatch', im)
        cv2.waitKey(100)

    # pid, process_handle = open_obs()
    # if not pid:
    #     return
    #
    # oldhash = None
    # while True:
    #     if oldhash is not None:
    #         logger.setLevel(logging.INFO)
    #
    #     sources = get_sources(pid, process_handle)
    #     logger.debug('Got sources %s', [s[0] for s in sources])
    #
    #     # return
    #
    #     game_captures = [
    #         OBSGameCapture(process_handle, _read_ptr(process_handle, addr + offsets['SOURCE_DATA_OFFSET']), offsets)
    #         for (name, typ, addr, offsets)
    #         in sources
    #         if typ == 'game_capture'
    #     ]
    #     logger.debug('Got game captures: %s', game_captures)
    #     overwatch_captures = [gc for gc in game_captures if gc.title == 'Overwatch']
    #     logger.debug('Got OW captures: %s', overwatch_captures)
    #
    #     overwatch_capture = get_gamecapture_matching(pid, process_handle, 'Overwatch')
    #     if not overwatch_capture:
    #         return
    #
    #     if hash(overwatch_capture) != oldhash:
    #         print(overwatch_capture)
    #         oldhash = hash(overwatch_capture)
    #
    #     im = overwatch_capture.read_texture()
    #     # close_obs(process_handle)
    #     if im is None:
    #         logger.warning('Failed to get image')
    #         time.sleep(1)
    #     else:
    #         im = cv2.resize(im, (1440, 810))
    #         cv2.imshow('overwatch', im)
    #         cv2.waitKey(1)
    #         time.sleep(0.3)


if __name__ == '__main__':
    main()
