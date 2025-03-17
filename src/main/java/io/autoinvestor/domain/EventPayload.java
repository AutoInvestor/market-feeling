package io.autoinvestor.domain;

import java.util.Map;

public interface EventPayload {
    Map<String, Object> asMap();
}
