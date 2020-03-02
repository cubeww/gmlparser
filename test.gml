do {
    with instance_create(100, 200, apple) {
        x += 1;
    }
} until (instance_number(apple) > 10);