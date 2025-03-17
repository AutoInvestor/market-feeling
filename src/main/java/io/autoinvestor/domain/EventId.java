package io.autoinvestor.domain;

public class EventId extends Id {
    EventId(String id) {
        super(id);
    }

    public static EventId generate() {
        return new EventId(generateId());
    }
}
