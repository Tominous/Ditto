# Copyright Arthurdw 2021-present
# Full MIT License can be found in `LICENSE` at the project root.

from __future__ import annotations

from os import getenv
from typing import TYPE_CHECKING

from cassandra.cluster import Cluster

from . import Webhook
from .db_statements import stmt

if TYPE_CHECKING:
    from uuid import UUID


class ScyllaDB:
    keyspace = 'ditto'

    def __init__(self):
        self.hosts = [host.strip().lower() for host in getenv("DB_HOST").split(',')]
        self.cluster = Cluster(self.hosts)
        self.session = self.cluster.connect()
        self.__setup_db()
        self.__prepare_statements()

    def __setup_db(self):
        statement = stmt.keyspace_init.format(keyspace=self.keyspace)
        self.session.execute(statement)
        self.session.set_keyspace(self.keyspace)
        self.session.execute(stmt.webhooks.init)

    def __prepare_statements(self):
        stmt.webhooks.create = self.session.prepare(stmt.webhooks.create)
        stmt.webhooks.get = self.session.prepare(stmt.webhooks.get)
        stmt.webhooks.delete = self.session.prepare(stmt.webhooks.delete)
        stmt.webhooks.add_role_mention = self.session.prepare(stmt.webhooks.add_role_mention)
        stmt.webhooks.remove_role_mention = self.session.prepare(stmt.webhooks.remove_role_mention)
        stmt.webhooks.add_user_mention = self.session.prepare(stmt.webhooks.add_user_mention)
        stmt.webhooks.remove_user_mention = self.session.prepare(stmt.webhooks.remove_user_mention)

    def create_webhook(self, webhook: Webhook):
        self.session.execute(stmt.webhooks.create, webhook.serialize())

    def get_webhook(self, webhook_id: UUID) -> Webhook:
        fetch = self.session.execute(stmt.webhooks.get, (webhook_id,))
        if result := fetch.one():
            print(result, '-------', type(result))
            return Webhook(*result)

        raise IndexError


DB = ScyllaDB
