import pluggy
from py_handoff.interface import BaseMessage

hookspec = pluggy.HookspecMarker("py_handoff")
hookimpl = pluggy.HookimplMarker("py_handoff")


class PyHandoffPluginSpec:
    @hookspec
    def capture_state(self) -> BaseMessage:
        """Define how to capture the state that you want to share with the remote

        Returns:
            BaseMessage: Captured state
        """

    @hookspec
    def restore_state(self, msg: BaseMessage):
        """Define how to restore the state at the remote side

        Args:
            msg (BaseMessage): [description]
        """
