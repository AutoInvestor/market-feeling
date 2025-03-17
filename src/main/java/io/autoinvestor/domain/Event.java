package io.autoinvestor.domain;

import java.util.Date;

public abstract class Event<EventPayload> {
    private final EventId id;
    private final Id aggregateId;
    private final String type;
    private final EventPayload payload;
    private final Date occurredAt;
    private final int version;

    protected Event(Id aggregateId, String type, EventPayload payload) {
        this(aggregateId, type, payload, 1);
    }

    protected Event(Id aggregateId, String type, EventPayload payload, int version) {
        this.id = EventId.generate();
        this.aggregateId = aggregateId;
        this.type = type;
        this.payload = payload;
        this.occurredAt = new Date();
        this.version = version;
    }

    public EventId getId() {
        return id;
    }

    public Id getAggregateId() {
        return aggregateId;
    }

    public String getType() {
        return type;
    }

    public EventPayload getPayload() {
        return payload;
    }

    public Date getOccurredAt() {
        return occurredAt;
    }

    public int getVersion() {
        return version;
    }
}
