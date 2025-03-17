package io.autoinvestor.domain;

import java.util.List;

public interface EventPublisher {
    void publish(List<Event<?>> events);
}
