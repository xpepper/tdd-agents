```python
def test_rover_moves_forward_north_from_initial_position():
    # Arrange
    plateau = (5, 5)
    initial_position = (1, 2, 'N')
    commands = "M"
    
    # Act
    result = execute_commands(plateau, initial_position, commands)
    
    # Assert
    assert result == (1, 3, 'N')
```

```python
def test_rover_rotate_left_from_north_to_west():
    """Test that a rover rotates left from North to West"""
    # This test will fail because no rover class or rotation functionality exists yet
    from mars_rover import Rover, Heading
    
    rover = Rover(x=0, y=0, heading=Heading.N)
    rover.rotate_left()
    
    assert rover.heading == Heading.W
```