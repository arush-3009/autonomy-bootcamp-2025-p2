"""
Heartbeat receiving logic.
"""

from pymavlink import mavutil

from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
DISCONNECT_THRESHOLD = 5

class HeartbeatReceiver:
    """
    HeartbeatReceiver class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        max_missed_heartbeat_count: int,
        local_logger: logger.Logger,
    ):
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """
        current_state = "Disconnected"
        
        if connection is None:
            local_logger.error("Failed to create Heartbeat receiver. No connection provided.", True)
            return False, None

        return cls(cls.__private_key, connection, local_logger, current_state, max_missed_heartbeat_count)
        

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
        current_state,
        max_missed_heartbeat_limit
    ) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"

        # Do any intializiation here
        self.__connection = connection
        self.__local_logger = local_logger
        
        self.__current_state = current_state
        self.__missed_heartbeat_count = 0
        self.__max_missed_heartbeat_count = max_missed_heartbeat_limit

    def run(
        self,
        args,  # Put your own arguments here
    ):
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """
        pass


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
