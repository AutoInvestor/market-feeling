import json
import threading
import traceback
from typing import Optional

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.futures import StreamingPullFuture
from google.cloud.pubsub_v1.subscriber.message import Message

from stock_api.application.companies.register_company_command_handler import (
    RegisterCompanyCommandHandler,
    RegisterCompanyCommand,
)
from stock_api.infrastructure.listeners.pubsub_mapper import PubSubEventMapper
from stock_api.logger import get_logger

logger = get_logger(__name__)


class PubSubCompaniesEventSubscriber:
    def __init__(
        self,
        command_handler: RegisterCompanyCommandHandler,
        project_id: str,
        subscription: str,
    ):
        self._command_handler = command_handler
        self._client = pubsub_v1.SubscriberClient()
        self._sub_path = self._client.subscription_path(project_id, subscription)
        self._future: Optional[StreamingPullFuture] = None

    def _callback(self, message: Message) -> None:
        try:
            raw = json.loads(message.data.decode("utf-8"))

            event = PubSubEventMapper.from_dict(raw)
            if event.type == "ASSET_CREATED":
                cmd = RegisterCompanyCommand(
                    id=event.aggregate_id,
                    ticker=event.payload.get("ticker"),
                    name=event.payload.get("name"),
                )
                self._command_handler.handle(cmd)

            message.ack()
        except Exception as e:
            logger.exception(
                "Error handling Pub/Sub message: %s: %s\n%s",
                type(e).__name__,
                str(e),
                traceback.format_exc(),
            )
            message.nack()

    def listen(self) -> None:
        def _run():
            self._future = self._client.subscribe(
                self._sub_path,
                callback=self._callback,
            )
            self._future.result()

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def stop(self) -> None:
        if self._future:
            self._future.cancel()
