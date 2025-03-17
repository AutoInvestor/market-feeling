package io.autoinvestor.infrastructure;

import io.autoinvestor.domain.Event;
import io.autoinvestor.domain.EventPublisher;
import java.util.ArrayList;
import java.util.List;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Component;

@Component
public class InMemoryEventPublisher implements EventPublisher {

    private final ApplicationEventPublisher eventPublisher;
    private final List<Event<?>> publishedEvents = new ArrayList<>();

    public InMemoryEventPublisher(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }

    @Override
    public void publish(List<Event<?>> events) {
        this.publishedEvents.addAll(events);
        events.forEach(this.eventPublisher::publishEvent);
    }

    public boolean hasPublishedEvent(String type, String aggregateId) {
        return publishedEvents.stream()
                .anyMatch(event -> event.getType().equals(type) && event.getAggregateId().value().equals(aggregateId));
    }
}
