def test_members_read_their_groups(org):
    assert org.can_read("ann", "team-a")
    assert not org.can_read("ann", "team-b")


def test_personal_brains_are_owner_only(org):
    assert org.can_read("ann", "personal/ann")
    assert not org.can_read("ben", "personal/ann")
    assert not org.can_write("ben", "personal/ann")


def test_write_lists_restrict_writers(org):
    assert org.can_read("ben", "handbook")
    assert not org.can_write("ben", "handbook")
    assert org.can_write("ann", "handbook")
    assert org.writable_groups("ben") == ["team-b"]
