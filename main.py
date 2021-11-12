from loguru import logger
import numba
from numba import jit

import test


def logInfo():
    logger.info(f"numba version: {numba.__version__}")


def main():
    test.run_test()


if __name__ == '__main__':
    print()
    main()
