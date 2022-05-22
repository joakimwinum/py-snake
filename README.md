# Python Snake CLI Game

This is a CLI game written in Python 3.6 and ported from PHP.

The game uses **WASD** for movements.

The objective of the game is to collect food dots and collect as much points as possible.

During the game, a developer mode can be activated that contains additional testing functionality.

There is a custom game engine class inside the game that takes care of mainly three things:
* clearing the screen (supports multiple OS)
* syncing the game loop (to a predefined FPS)
* detecting key presses

The PHP version of the game can be found [here](https://github.com/joakimwinum/php-snake).

## Usage

Run the game in a CLI:

```console
docker run -it --rm --name python-snake joakimwinum/python-snake
```

## Authors

* **Joakim Winum Lien** - *Initial work* - [joakimwinum](https://github.com/joakimwinum)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/joakimwinum/python-snake/blob/main/LICENSE) file for details
