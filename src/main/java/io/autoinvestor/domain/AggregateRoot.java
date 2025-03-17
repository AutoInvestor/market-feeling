package io.autoinvestor.domain;

import java.util.ArrayList;
import java.util.List;

public class AggregateRoot {
    private final List<Event<?>> events;

    public AggregateRoot() {
        this.events = new ArrayList<>();
    }

    protected void recordEvent(Event<? extends EventPayload> event) {
        this.events.add(event);
    }

    public List<Event<?>> releaseEvents() {
        List<Event<?>> events = new ArrayList<>(this.events);
        this.events.clear();
        return events;
    }
}
