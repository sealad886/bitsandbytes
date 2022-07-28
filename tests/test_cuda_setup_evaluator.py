import pytest

from typing import List

from bitsandbytes.cuda_setup import (
    CUDA_RUNTIME_LIB,
    get_cuda_runtime_lib_path,
    evaluate_cuda_setup,
    tokenize_paths,
)


HAPPY_PATH__LD_LIB_TEST_PATHS: List[tuple[str,str]] = [
    (f"some/other/dir:dir/with/{CUDA_RUNTIME_LIB}", f"dir/with/{CUDA_RUNTIME_LIB}"),
    (f":some/other/dir:dir/with/{CUDA_RUNTIME_LIB}", f"dir/with/{CUDA_RUNTIME_LIB}"),
    (f"some/other/dir:dir/with/{CUDA_RUNTIME_LIB}:", f"dir/with/{CUDA_RUNTIME_LIB}"),
    (f"some/other/dir::dir/with/{CUDA_RUNTIME_LIB}", f"dir/with/{CUDA_RUNTIME_LIB}"),
    (f"dir/with/{CUDA_RUNTIME_LIB}:some/other/dir", f"dir/with/{CUDA_RUNTIME_LIB}"),
]


@pytest.mark.parametrize(
    "test_input, expected",
    HAPPY_PATH__LD_LIB_TEST_PATHS
)
def test_get_cuda_runtime_lib_path__happy_path(
        tmp_path, test_input: str, expected: str
):
    for path in tokenize_paths(test_input):
        assert False == tmp_path / test_input
        test_dir.mkdir()
        (test_input / CUDA_RUNTIME_LIB).touch()
    assert get_cuda_runtime_lib_path(test_input) == expected


UNHAPPY_PATH__LD_LIB_TEST_PATHS = [
    f"a/b/c/{CUDA_RUNTIME_LIB}:d/e/f/{CUDA_RUNTIME_LIB}",
    f"a/b/c/{CUDA_RUNTIME_LIB}:d/e/f/{CUDA_RUNTIME_LIB}:g/h/j/{CUDA_RUNTIME_LIB}",
]


@pytest.mark.parametrize("test_input", UNHAPPY_PATH__LD_LIB_TEST_PATHS)
def test_get_cuda_runtime_lib_path__unhappy_path(tmp_path, test_input: str):
    test_input = tmp_path / test_input
    (test_input / CUDA_RUNTIME_LIB).touch()
    with pytest.raises(FileNotFoundError) as err_info:
        get_cuda_runtime_lib_path(test_input)
    assert all(
        match in err_info 
        for match in {"duplicate", CUDA_RUNTIME_LIB}
    )


def test_get_cuda_runtime_lib_path__non_existent_dir(capsys, tmp_path):
    existent_dir = tmp_path / 'a/b'
    existent_dir.mkdir()
    non_existent_dir = tmp_path / 'c/d' # non-existent dir
    test_input = ":".join([str(existent_dir), str(non_existent_dir)])

    get_cuda_runtime_lib_path(test_input)
    std_err = capsys.readouterr().err

    assert all(
        match in std_err 
        for match in {"WARNING", "non-existent"}
    )