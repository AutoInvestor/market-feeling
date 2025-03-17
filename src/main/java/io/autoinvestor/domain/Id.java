package io.autoinvestor.domain;

import java.util.Objects;
import java.util.UUID;

public abstract class Id {
    private final String id;

    public Id(String id) {
        this.id = id;
    }

    public String value() {
        return id;
    }

    protected static String generateId() {
        return UUID.randomUUID().toString();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o)
            return true;
        if (!(o instanceof Id that))
            return false;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}
