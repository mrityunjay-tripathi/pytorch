# @lint-ignore-every PYTHON3COMPATIMPORTS

r"""
The torch package contains data structures for multi-dimensional
tensors and mathematical operations over these are defined.
Additionally, it provides many utilities for efficient serializing of
Tensors and arbitrary types, and other useful utilities.

It has a CUDA counterpart, that enables you to run your tensor computations
on an NVIDIA GPU with compute capability >= 3.0.
"""

import os
import sys
import platform
import ctypes
from ._utils import _import_dotted_name
from ._utils_internal import get_file_path, prepare_multiprocessing_environment
from .version import __version__
from ._six import string_classes as _string_classes

__all__ = [
    'typename', 'is_tensor', 'is_storage', 'set_default_tensor_type',
    'set_rng_state', 'get_rng_state', 'manual_seed', 'initial_seed', 'seed',
    'save', 'load', 'set_printoptions', 'chunk', 'split', 'stack', 'matmul',
    'no_grad', 'enable_grad', 'rand', 'randn',
    'DoubleStorage', 'FloatStorage', 'LongStorage', 'IntStorage',
    'ShortStorage', 'CharStorage', 'ByteStorage', 'BoolStorage',
    'DoubleTensor', 'FloatTensor', 'LongTensor', 'IntTensor',
    'ShortTensor', 'CharTensor', 'ByteTensor', 'BoolTensor', 'Tensor',
]

################################################################################
# Load the extension module
################################################################################

if platform.system() == 'Windows':
    NVTOOLSEXT_PATH = os.getenv('NVTOOLSEXT_PATH', 'C:\\Program Files\\NVIDIA Corporation\\NvToolsExt')

    if os.path.exists(NVTOOLSEXT_PATH):
        nvtoolsext_lib_path = os.path.join(NVTOOLSEXT_PATH, 'bin', 'x64')
    else:
        nvtoolsext_lib_path = ''

    py_dll_path = os.path.join(sys.exec_prefix, 'Library', 'bin')
    th_dll_path = os.path.join(os.path.dirname(__file__), 'lib')

    dll_paths = [th_dll_path, py_dll_path, nvtoolsext_lib_path, os.environ['PATH']]

    # then add the path to env
    os.environ['PATH'] = ';'.join(dll_paths)


# See Note [Global dependencies]
def _load_global_deps():
    if platform.system() == 'Windows':
        return

    lib_name = 'libtorch_global_deps' + ('.dylib' if platform.system() == 'Darwin' else '.so')
    here = os.path.abspath(__file__)
    lib_path = os.path.join(os.path.dirname(here), 'lib', lib_name)

    ctypes.CDLL(lib_path, mode=ctypes.RTLD_GLOBAL)


# See Note [Global dependencies]
_load_global_deps()

from torch._C import *

__all__ += [name for name in dir(_C)
            if name[0] != '_' and
            not name.endswith('Base')]

################################################################################
# Define basic utilities
################################################################################


def typename(o):
    if isinstance(o, torch.Tensor):
        return o.type()

    module = ''
    class_name = ''
    if hasattr(o, '__module__') and o.__module__ != 'builtins' \
            and o.__module__ != '__builtin__' and o.__module__ is not None:
        module = o.__module__ + '.'

    if hasattr(o, '__qualname__'):
        class_name = o.__qualname__
    elif hasattr(o, '__name__'):
        class_name = o.__name__
    else:
        class_name = o.__class__.__name__

    return module + class_name


def is_tensor(obj):
    r"""Returns True if `obj` is a PyTorch tensor.

    Args:
        obj (Object): Object to test
    """
    return isinstance(obj, torch.Tensor)


def is_storage(obj):
    r"""Returns True if `obj` is a PyTorch storage object.

    Args:
        obj (Object): Object to test
    """
    return type(obj) in _storage_classes


def set_default_tensor_type(t):
    r"""Sets the default ``torch.Tensor`` type to floating point tensor type
    ``t``. This type will also be used as default floating point type for
    type inference in :func:`torch.tensor`.

    The default floating point tensor type is initially ``torch.FloatTensor``.

    Args:
        t (type or string): the floating point tensor type or its name

    Example::

        >>> torch.tensor([1.2, 3]).dtype    # initial default for floating point is torch.float32
        torch.float32
        >>> torch.set_default_tensor_type(torch.DoubleTensor)
        >>> torch.tensor([1.2, 3]).dtype    # a new floating point tensor
        torch.float64

    """
    if isinstance(t, _string_classes):
        t = _import_dotted_name(t)
    _C._set_default_tensor_type(t)


def set_default_dtype(d):
    r"""Sets the default floating point dtype to :attr:`d`. This type will be
    used as default floating point type for type inference in
    :func:`torch.tensor`.

    The default floating point dtype is initially ``torch.float32``.

    Args:
        d (:class:`torch.dtype`): the floating point dtype to make the default

    Example::

        >>> torch.tensor([1.2, 3]).dtype           # initial default for floating point is torch.float32
        torch.float32
        >>> torch.set_default_dtype(torch.float64)
        >>> torch.tensor([1.2, 3]).dtype           # a new floating point tensor
        torch.float64

    """
    _C._set_default_dtype(d)

# If you edit these imports, please update torch/__init__.py.in as well
from .random import set_rng_state, get_rng_state, manual_seed, initial_seed, seed
from .serialization import save, load
from ._tensor_str import set_printoptions

################################################################################
# Define Storage and Tensor classes
################################################################################

from .tensor import Tensor
from .storage import _StorageBase


class DoubleStorage(_C.DoubleStorageBase, _StorageBase):
    pass


class FloatStorage(_C.FloatStorageBase, _StorageBase):
    pass


class HalfStorage(_C.HalfStorageBase, _StorageBase):
    pass


class LongStorage(_C.LongStorageBase, _StorageBase):
    pass


class IntStorage(_C.IntStorageBase, _StorageBase):
    pass


class ShortStorage(_C.ShortStorageBase, _StorageBase):
    pass


class CharStorage(_C.CharStorageBase, _StorageBase):
    pass


class ByteStorage(_C.ByteStorageBase, _StorageBase):
    pass


class BoolStorage(_C.BoolStorageBase, _StorageBase):
    pass


class BFloat16Storage(_C.BFloat16StorageBase, _StorageBase):
    pass


class QUInt8Storage(_C.QUInt8StorageBase, _StorageBase):
    pass

class QInt8Storage(_C.QInt8StorageBase, _StorageBase):
    pass

class QInt32Storage(_C.QInt32StorageBase, _StorageBase):
    pass


_storage_classes = {
    DoubleStorage, FloatStorage, LongStorage, IntStorage, ShortStorage,
    CharStorage, ByteStorage, HalfStorage, BoolStorage, QUInt8Storage, QInt8Storage,
    QInt32Storage, BFloat16Storage
}

# The _tensor_classes set is initialized by the call to _C._initialize_tensor_type_bindings()
_tensor_classes = set()


################################################################################
# Initialize extension
################################################################################

def manager_path():
    if platform.system() == 'Windows':
        return b""
    path = get_file_path('torch', 'bin', 'torch_shm_manager')
    prepare_multiprocessing_environment(get_file_path('torch'))
    if not os.path.exists(path):
        raise RuntimeError("Unable to find torch_shm_manager at " + path)
    return path.encode('utf-8')


# Shared memory manager needs to know the exact location of manager executable
_C._initExtension(manager_path())
del manager_path

for name in dir(_C._VariableFunctions):
    if name.startswith('__'):
        continue
    globals()[name] = getattr(_C._VariableFunctions, name)

################################################################################
# Import interface functions defined in Python
################################################################################

# needs to be after the above ATen bindings so we can overwrite from Python side
from .functional import *


################################################################################
# Remove unnecessary members
################################################################################

del DoubleStorageBase
del FloatStorageBase
del LongStorageBase
del IntStorageBase
del ShortStorageBase
del CharStorageBase
del ByteStorageBase
del BoolStorageBase
del QUInt8StorageBase
del BFloat16StorageBase

################################################################################
# Import most common subpackages
################################################################################

import torch.cuda
import torch.autograd
from torch.autograd import no_grad, enable_grad, set_grad_enabled
import torch.nn
import torch.nn.intrinsic
import torch.nn.quantized
import torch.optim
import torch.multiprocessing
import torch.sparse
import torch.utils.backcompat
import torch.onnx
import torch.jit
import torch.hub
import torch.random
import torch.distributions
import torch.testing
import torch.backends.cuda
import torch.backends.mkl
import torch.backends.openmp
import torch.backends.quantized
import torch.quantization
import torch.utils.data
import torch.__config__
import torch.__future__

_C._init_names(list(torch._storage_classes))

# attach docstrings to torch and tensor functions
from . import _torch_docs, _tensor_docs, _storage_docs
del _torch_docs, _tensor_docs, _storage_docs


def compiled_with_cxx11_abi():
    r"""Returns whether PyTorch was built with _GLIBCXX_USE_CXX11_ABI=1"""
    return _C._GLIBCXX_USE_CXX11_ABI


# Import the ops "namespace"
from torch._ops import ops
from torch._classes import classes

# Import the quasi random sampler
import torch.quasirandom

# If you are seeing this, it means that this call site was not checked if
# the memory format could be preserved, and it was switched to old default
# behaviour of contiguous
legacy_contiguous_format = contiguous_format

# Register fork handler to initialize OpenMP in child processes (see gh-28389)
from torch.multiprocessing._atfork import register_after_fork
register_after_fork(torch.get_num_threads)
del register_after_fork
