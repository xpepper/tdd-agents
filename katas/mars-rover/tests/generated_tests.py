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