

import logging
import multiprocessing
from typing import Tuple


class SpawnerUtils:
    
    
    @classmethod
    def calc_workers_amount(cls) -> Tuple[int, int]:
        '''
        @retval:
            (healthy_workers_amount, unhealthy_workers_amount)
        '''
        cpu_cores = multiprocessing.cpu_count()
        if not cpu_cores:
            logging.error('This should not ever happen.')
            raise Exception('This should not ever happen.')
        if cpu_cores > 4 and cpu_cores <= 7:

            return ( int(cpu_cores * 1.25) - 1, 1 )
        elif cpu_cores >= 8:

            return ( int(cpu_cores * 1.5) - 2, 2 )

        return (cpu_cores, 0)
