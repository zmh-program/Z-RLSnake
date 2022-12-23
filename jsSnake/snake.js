/* Polyfill */
(function(){ 'use strict';
    let lastTime = 0;
    const vendors = ['webkit', 'moz'];
    for(let x = 0; x < vendors.length && !window.requestAnimationFrame; ++x ) {
        window.requestAnimationFrame = window[ vendors[ x ] + 'RequestAnimationFrame' ];
        window.cancelAnimationFrame = window[ vendors[ x ] + 'CancelAnimationFrame' ] || window[ vendors[ x ] + 'CancelRequestAnimationFrame' ];
    }
    if( !window.requestAnimationFrame ) {
        window.requestAnimationFrame.bind(function( callback, element ) {
            const currTime = new Date().getTime();
            const timeToCall = Math.max(0, 16 - (currTime - lastTime));
            const id = window.setTimeout(
                    function () {
                        callback(currTime + timeToCall);
                    }, timeToCall);
            lastTime = currTime + timeToCall;
            return id;
        });
    }
    if( !window.cancelAnimationFrame ) {
        window.cancelAnimationFrame = id => (clearTimeout( id ));
    }
})();

/* Core */

game = {};

(function(){
    'use strict';

    game.math = Math;
    game.mathProps = 'E LN10 LN2 LOG2E LOG10E PI SQRT1_2 SQRT2 abs acos asin atan ceil cos exp floor log round sin sqrt tan atan2 pow max min'.split( ' ' );
    for (let i = 0; i < game.mathProps.length; i++ )(game[game.mathProps[i]] = game.math[ game.mathProps[i]])
    game.is_set = prop => (typeof prop != 'undefined');
    game.log = function() {
        if( game.is_set( game.config ) && game.config.debug && window.console ){
            console.log( Array.prototype.slice.call( arguments ) );
        }
    };

})();

/* Group */

(function(){ 
    'use strict';
    
    game.Group = function() {
        this.collection = [];
        this.length = 0;
    };

    game.Group.prototype.add = function(item ) {
        this.collection.push( item );
        this.length++;
    };

    game.Group.prototype.remove = function(index ) {
        if( index < this.length ) {
            this.collection.splice( index, 1 );
            this.length--;
        }
    };

    game.Group.prototype.empty = function() {
        this.collection.length = 0;
        this.length = 0;
    };

    game.Group.prototype.each = function(action, asc=0 ) {
        if(asc) {
            for(let i = 0; i < this.length; i++) {
                this.collection[i][action](i);
            }
        } else {
            let i = this.length;
            while(i--) (this.collection[i][action](i));
        }
    };
})();

/* Utilities */
(function(){ 'use strict';
    game.util = {
        randn: (min, max) => (game.math.random() * ( max - min ) + min),
        randInt: (min, max ) => (game.math.floor( game.math.random() * ( max - min + 1) ) + min),
    };
}());

/* State */
(function(){ 'use strict';
    game.states = {};
    game.addState = state => (game.states[state.name] = state)
    game.setState = name => {
        if(game.state) (
            game.states[ game.state ].exit()
        );
        game.state = name;
        game.states[ game.state ].init();
    };
    game.currentState = () => (game.states[game.state]);
}());

/* Time */
(function(){ 
    'use strict';
    game.Time = function() {
        this.reset();
    }

    game.Time.prototype.reset = function() {
        this.now = Date.now();
        this.last = Date.now();
        this.delta = 60;
        this.ndelta = 1;
        this.elapsed = 0;
        this.tick = 0;
    };

    game.Time.prototype.update = function() {
        this.now = Date.now();
        this.delta = this.now - this.last;
        this.ndelta = Math.min( Math.max( this.delta / ( 1000 / 60 ), 0.0001 ), 10 );
        this.elapsed += this.delta;
        this.last = this.now;
        this.tick++;
    };
})();

/* Grid Entity */

(function(){ 
    'use strict';
    game.Grid = function(cols, rows ) {
        this.cols = cols;
        this.rows = rows;
        this.tiles = [];
        for(let x = 0; x < cols; x++) {
            this.tiles[x] = [];
            for(let y = 0; y<rows; y++) {this.tiles[ x ].push( 'empty' )}
        }
    };

    game.Grid.prototype.get = function(x, y ) {
        return this.tiles[ x ][ y ];
    };

    game.Grid.prototype.set = function(x, y, val ) {
        this.tiles[ x ][ y ] = val;
    };

})();

/* Board Tile Entity */

(function(){ 'use strict';

    game.BoardTile = function(opt ) {
        this.parentState = opt.parentState;
        this.parentGroup = opt.parentGroup;
        this.col = opt.col;
        this.row = opt.row;
        this.x = opt.x;
        this.y = opt.y;
        this.width = opt.w;
        this.height = opt.h;
        this.elem = document.createElement( 'div' );
        this.elem.style.position = 'absolute';
        this.elem.className = 'tile';
        this.parentState.stageElem.appendChild( this.elem );
        this.classes = {
            pressed: 0,
            path: 0,
            up: 0,
            down: 0,
            left: 0,
            right: 0
        }
        this.updateDimensions();
    };

    game.BoardTile.prototype.update = function() {
        for(const k in this.classes ) {
            if( this.classes[ k ] ) {
                this.classes[ k ]--;
            }
        }

        if( this.parentState.food.tile.col === this.col || this.parentState.food.tile.row === this.row ) {
            this.classes.path = 1;
            if( this.col < this.parentState.food.tile.col ) {
                this.classes.right = 1;
            } else {
                this.classes.right = 0;
            }
            if( this.col > this.parentState.food.tile.col ) {
                this.classes.left = 1;
            } else {
                this.classes.left = 0;
            }
            if( this.row > this.parentState.food.tile.row ) {
                this.classes.up = 1;
            } else {
                this.classes.up = 0;
            }
            if( this.row < this.parentState.food.tile.row ) {
                this.classes.down = 1;
            } else {
                this.classes.down = 0;
            }
        } else {
            this.classes.path = 0;
        }

        if( this.parentState.food.eaten ) {
            this.classes.path = 0;
        }
    };

    game.BoardTile.prototype.updateDimensions = function() {
        this.x = this.col * this.parentState.tileWidth;
        this.y = this.row * this.parentState.tileHeight;
        this.width = this.parentState.tileWidth - this.parentState.spacing;
        this.height = this.parentState.tileHeight - this.parentState.spacing;
        this.elem.style.left = this.x + 'px';
        this.elem.style.top = this.y + 'px';
        this.elem.style.width = this.width + 'px';
        this.elem.style.height = this.height + 'px';
    };

    game.BoardTile.prototype.render = function() {
        let classString = '';
        for(const k in this.classes) {if( this.classes[ k ] ) {classString += k + ' '}}
        this.elem.className = 'tile ' + classString;
    };

})();

/* Snake Tile Entity */

(function(){ 'use strict';

    game.SnakeTile = function(opt ) {
        this.parentState = opt.parentState;
        this.parentGroup = opt.parentGroup;
        this.col = opt.col;
        this.row = opt.row;
        this.x = opt.x;
        this.y = opt.y;
        this.width = opt.w;
        this.height = opt.h;
        this.color = null;
        this.scale = 1;
        this.rotation = 0;
        this.blur = 0;
        this.alpha = 1;
        this.borderRadius = 0;
        this.borderRadiusAmount = 0;
        this.elem = document.createElement( 'div' );
        this.elem.style.position = 'absolute';
        this.parentState.stageElem.appendChild( this.elem );
    };

    game.SnakeTile.prototype.update = function(i ) {
        this.x = this.col * this.parentState.tileWidth;
        this.y = this.row * this.parentState.tileHeight;
        if( i === 0 ) {
            this.color = '#fff';
            this.blur = this.parentState.dimAvg * 0.03 + Math.sin( this.parentState.time.elapsed / 200 ) * this.parentState.dimAvg * 0.015;
            if( this.parentState.snake.dir === 'n' ) {
                this.borderRadius = this.borderRadiusAmount + '% ' + this.borderRadiusAmount + '% 0 0';
            } else if( this.parentState.snake.dir === 's' ) {
                this.borderRadius = '0 0 ' + this.borderRadiusAmount + '% ' + this.borderRadiusAmount + '%';
            } else if( this.parentState.snake.dir === 'e' ) {
                this.borderRadius = '0 ' + this.borderRadiusAmount + '% ' + this.borderRadiusAmount + '% 0';
            } else if( this.parentState.snake.dir === 'w' ) {
                this.borderRadius = this.borderRadiusAmount + '% 0 0 ' + this.borderRadiusAmount + '%';
            }
        } else {
            this.color = '#fff';
            this.blur = 0;
            this.borderRadius = '0';
        }
        this.alpha = 1 - ( i / this.parentState.snake.tiles.length ) * 0.6;
        this.rotation = ( this.parentState.snake.justAteTick / this.parentState.snake.justAteTickMax ) * 90;
        this.scale = 1 + (this.parentState.snake.justAteTick / this.parentState.snake.justAteTickMax);
    };

    game.SnakeTile.prototype.updateDimensions = function() {
        this.width = this.parentState.tileWidth - this.parentState.spacing;
        this.height = this.parentState.tileHeight - this.parentState.spacing;
    };

    game.SnakeTile.prototype.render = function() {
        this.elem.style.left = this.x + 'px';
        this.elem.style.top = this.y + 'px';
        this.elem.style.width = this.width + 'px';
        this.elem.style.height = this.height + 'px';
        this.elem.style.backgroundColor = 'rgba(255, 255, 255, ' + this.alpha + ')';
        this.elem.style.boxShadow = '0 0 ' + this.blur + 'px #fff';
        this.elem.style.borderRadius = `${this.borderRadius} px`;
    };
})();

/* Food Tile Entity */

(function(){ 'use strict';

    game.FoodTile = function(opt ) {
        this.parentState = opt.parentState;
        this.parentGroup = opt.parentGroup;
        this.col = opt.col;
        this.row = opt.row;
        this.x = opt.x;
        this.y = opt.y;
        this.width = opt.w;
        this.height = opt.h;
        this.blur = 0;
        this.scale = 1;
        this.heightue = 100;
        this.opacity = 0;
        this.elem = document.createElement( 'div' );
        this.elem.style.position = 'absolute';
        this.parentState.stageElem.appendChild( this.elem );
    };

    game.FoodTile.prototype.update = function() {
        this.x = this.col * this.parentState.tileWidth;
        this.y = this.row * this.parentState.tileHeight;
        this.blur = this.parentState.dimAvg * 0.03 + Math.sin( this.parentState.time.elapsed / 200 ) * this.parentState.dimAvg * 0.015;
        this.scale = 0.8 + Math.sin( this.parentState.time.elapsed / 200 ) * 0.2;

        if( this.parentState.food.birthTick || this.parentState.food.deathTick ) {
            if( this.parentState.food.birthTick ) {
                this.opacity = 1 - (this.parentState.food.birthTick);
            } else {
                this.opacity = (this.parentState.food.deathTick);
            }
        } else {
            this.opacity = 1;
        }
    };

    game.FoodTile.prototype.updateDimensions = function() {
        this.width = this.parentState.tileWidth - this.parentState.spacing;
        this.height = this.parentState.tileHeight - this.parentState.spacing;
    };

    game.FoodTile.prototype.render = function() {
        this.elem.style.left = this.x + 'px';
        this.elem.style.top = this.y + 'px';
        this.elem.style.width = this.width + 'px';
        this.elem.style.height = this.height + 'px';
        this.elem.style[ 'transform' ] = 'translateZ(0) scale(' + this.scale + ')';
        this.elem.style.backgroundColor = 'hsla(' + this.heightue + ', 100%, 60%, 1)';
        this.elem.style.boxShadow = `0 0 ${this.blur}px hsla(${this.heightue}, 100%, 60%, 1)`;
        this.elem.style.opacity = this.opacity;
    };

})();

/* Snake Entity */

(function(){ 'use strict';

    game.Snake = function(opt ) {
        let i;
        this.parentState = opt.parentState;
        this.dir = 'e';
        this.currDir = this.dir;
        this.tiles = [];
        for(i = 0; i < 5; i++ ) {
            this.tiles.push( new game.SnakeTile({
                parentState: this.parentState,
                parentGroup: this.tiles,
                col: 8 - i,
                row: 3,
                x: ( 8 - i ) * opt.parentState.tileWidth,
                y: 3 * opt.parentState.tileHeight,
                w: opt.parentState.tileWidth - opt.parentState.spacing,
                h: opt.parentState.tileHeight - opt.parentState.spacing
            }));
        }
        this.last = 0;
        this.updateTick = 10;
        this.updateTickMax = this.updateTick;
        this.updateTickLimit = 3;
        this.updateTickChange = 0.2;
        this.deathFlag = 0;
        this.justAteTick = 0;
        this.justAteTickMax = 1;
        this.justAteTickChange = 0.05;

        // sync data grid of the play state
        i = this.tiles.length;

        while( i-- ) {
            this.parentState.grid.set( this.tiles[ i ].col, this.tiles[ i ].row, 'snake' );
        }
    };

    game.Snake.prototype.updateDimensions = function() {
        let i = this.tiles.length;
        while( i-- ) {
            this.tiles[ i ].updateDimensions();
        }
    };

    game.Snake.prototype.update = function() {
        console.log(this.tiles)
        let i;
        if( this.parentState.keys.up ) {
            if( this.dir !== 's' && this.dir !== 'n' && this.currDir !== 's' && this.currDir !== 'n' ) {
                this.dir = 'n';
            }
        } else if( this.parentState.keys.down) {
            if( this.dir !== 'n' && this.dir !== 's' && this.currDir !== 'n' && this.currDir !== 's' ) {
                this.dir = 's';
            }
        } else if( this.parentState.keys.right ) {
            if( this.dir !== 'w' && this.dir !== 'e' && this.currDir !== 'w' && this.currDir !== 'e' ) {
                this.dir = 'e';
            }
        } else if( this.parentState.keys.left ) {
            if( this.dir !== 'e' && this.dir !== 'w' && this.currDir !== 'e' && this.currDir !== 'w' ) {
                this.dir = 'w';
            }
        }

        this.parentState.keys.up = 0;
        this.parentState.keys.down = 0;
        this.parentState.keys.right = 0;
        this.parentState.keys.left = 0;

        this.updateTick += this.parentState.time.ndelta;
        if( this.updateTick >= this.updateTickMax ) {
            // reset the update timer to 0, or whatever leftover there is
            this.updateTick = ( this.updateTick - this.updateTickMax );

            // rotate snake block array
            this.tiles.unshift( new game.SnakeTile({
                parentState: this.parentState,
                parentGroup: this.tiles,
                col: this.tiles[ 0 ].col,
                row: this.tiles[ 0 ].row,
                x: this.tiles[ 0 ].col * this.parentState.tileWidth,
                y: this.tiles[ 0 ].row * this.parentState.tileHeight,
                w: this.parentState.tileWidth - this.parentState.spacing,
                h: this.parentState.tileHeight - this.parentState.spacing
            }));
            this.last = this.tiles.pop();
            this.parentState.stageElem.removeChild( this.last.elem );

            this.parentState.boardTiles.collection[ this.last.col + ( this.last.row * this.parentState.cols ) ].classes.pressed = 2;

            // sync data grid of the play state
            i = this.tiles.length;

            while( i-- ) {
                this.parentState.grid.set( this.tiles[ i ].col, this.tiles[ i ].row, 'snake' );
            }
            this.parentState.grid.set( this.last.col, this.last.row, 'empty' );


            // move the snake's head
            if ( this.dir === 'n' ) {
                this.currDir = 'n';
                this.tiles[ 0 ].row -= 1;
            } else if( this.dir === 's' ) {
                this.currDir = 's';
                this.tiles[ 0 ].row += 1;
            } else if( this.dir === 'w' ) {
                this.currDir = 'w';
                this.tiles[ 0 ].col -= 1;
            } else if( this.dir === 'e' ) {
                this.currDir = 'e';
                this.tiles[ 0 ].col += 1;
            }

            // wrap walls
            this.widthallFlag = false;
            if( this.tiles[ 0 ].col >= this.parentState.cols ) {
                this.tiles[ 0 ].col = 0;
                this.widthallFlag = true;
            }
            if( this.tiles[ 0 ].col < 0 ) {
                this.tiles[ 0 ].col = this.parentState.cols - 1;
                this.widthallFlag = true;
            }
            if( this.tiles[ 0 ].row >= this.parentState.rows ) {
                this.tiles[ 0 ].row = 0;
                this.widthallFlag = true;
            }
            if( this.tiles[ 0 ].row < 0 ) {
                this.tiles[ 0 ].row = this.parentState.rows - 1;
                this.widthallFlag = true;
            }

            // check death by eating self
            if( this.parentState.grid.get( this.tiles[ 0 ].col, this.tiles[ 0 ].row ) === 'snake' ) {
                this.deathFlag = 1;
                clearTimeout( this.foodCreateTimeout );
            }

            // check eating of food
            if( this.parentState.grid.get( this.tiles[ 0 ].col, this.tiles[ 0 ].row ) === 'food' ) {
                this.tiles.push( new game.SnakeTile({
                    parentState: this.parentState,
                    parentGroup: this.tiles,
                    col: this.last.col,
                    row: this.last.row,
                    x: this.last.col * this.parentState.tileWidth,
                    y: this.last.row * this.parentState.tileHeight,
                    w: this.parentState.tileWidth - this.parentState.spacing,
                    h: this.parentState.tileHeight - this.parentState.spacing
                }));
                if( this.updateTickMax - this.updateTickChange > this.updateTickLimit ) {
                    this.updateTickMax -= this.updateTickChange;
                }
                this.parentState.score++;
                this.parentState.scoreElem.innerHTML = this.parentState.score;
                this.justAteTick = this.justAteTickMax;

                this.parentState.food.eaten = 1;
                this.parentState.stageElem.removeChild( this.parentState.food.tile.elem );

                const _this = this;

                this.foodCreateTimeout = setTimeout( function() {
                    _this.parentState.food = new game.Food({
                        parentState: _this.parentState
                    });
                }, 300);
            }

            // check death by eating self
            if( this.deathFlag ) {
                game.setState( 'play' );
            }
        }

        // update individual snake tiles
        i = this.tiles.length;
        while( i-- ) {
            this.tiles[ i ].update( i );
        }

        if( this.justAteTick > 0 ) {
            this.justAteTick -= this.justAteTickChange;
        } else if( this.justAteTick < 0 ) {
            this.justAteTick = 0;
        }
    };

    game.Snake.prototype.render = function() {
        // render individual snake tiles
        let i = this.tiles.length;
        while( i-- ) {
            this.tiles[ i ].render( i );
        }
    };

})();

/* Food Entity */

(function(){ 'use strict';

    game.Food = function(opt ) {
        this.parentState = opt.parentState;
        this.tile = new game.FoodTile({
            parentState: this.parentState,
            col: 0,
            row: 0,
            x: 0,
            y: 0,
            w: opt.parentState.tileWidth - opt.parentState.spacing,
            h: opt.parentState.tileHeight - opt.parentState.spacing
        });
        this.reset();
        this.eaten = 0;
        this.birthTick = 1;
        this.deathTick = 0;
        this.birthTickChange = 0.025;
        this.deathTickChange = 0.05;
    };

    game.Food.prototype.reset = function() {
        const empty = [];
        for(let x = 0; x < this.parentState.cols; x++) {
            for(let y = 0; y < this.parentState.rows; y++) {
                const tile = this.parentState.grid.get(x, y);
                if( tile === 'empty' ) {
                    empty.push( { x: x, y: y } );
                }
            }
        }
        const newTile = empty[game.util.randInt(0, empty.length - 1)];
        this.tile.col = newTile.x;
        this.tile.row = newTile.y;
    };

    game.Food.prototype.updateDimensions = function() {
        this.tile.updateDimensions();
    };

    game.Food.prototype.update = function() {
        // update food tile
        this.tile.update();

        if( this.birthTick > 0 ) {
            this.birthTick -= this.birthTickChange;
        } else if( this.birthTick < 0 ) {
            this.birthTick = 0;
        }

        // sync data grid of the play state
        this.parentState.grid.set( this.tile.col, this.tile.row, 'food' );
    };

    game.Food.prototype.render = function() {
        this.tile.render();
    };

})();

/* Play State */

(function(){ 
    'use strict';

    function StatePlay() {
        this.name = 'play';
    }

    StatePlay.prototype.init = function() {
        this.scoreElem = document.querySelector( '.score' );
        this.stageElem = document.querySelector( '.stage' );
        this.dimLong = 28;
        this.dimShort = 16;
        this.padding = 0.25;
        this.boardTiles = new game.Group();
        this.keys = {};
        this.foodCreateTimeout = null;
        this.score = 0;
        this.scoreElem.innerHTML = this.score;
        this.time = new game.Time();
        this.getDimensions();
        if( this.widthinWidth < this.widthinHeight ) {
            this.rows = this.dimLong;
            this.cols = this.dimShort;
        } else {
            this.rows = this.dimShort;
            this.cols = this.dimLong;
        }
        this.spacing = 1;
        this.grid = new game.Grid( this.cols, this.rows );
        this.resize();
        this.createBoardTiles();
        this.bindEvents();
        this.snake = new game.Snake({
            parentState: this
        });
        this.food = new game.Food({
            parentState: this
        });
    };

    StatePlay.prototype.getDimensions = function() {
        this.widthinWidth = window.innerWidth;
        this.widthinHeight = window.innerHeight;
        this.activeWidth = this.widthinWidth - ( this.widthinWidth * this.padding );
        this.activeHeight = this.widthinHeight - ( this.widthinHeight * this.padding );
    };

    StatePlay.prototype.resize = function() {
        const _this = game.currentState();
        _this.getDimensions();
        _this.stageRatio = _this.rows / _this.cols;

        if( _this.activeWidth > _this.activeHeight / _this.stageRatio ) {
            _this.stageHeight = _this.activeHeight;
            _this.stageElem.style.height = _this.stageHeight + 'px';
            _this.stageWidth = Math.floor( _this.stageHeight /_this.stageRatio );
            _this.stageElem.style.width = _this.stageWidth + 'px';
        } else {
            _this.stageWidth = _this.activeWidth;
            _this.stageElem.style.width = _this.stageWidth + 'px';
            _this.stageHeight = Math.floor( _this.stageWidth * _this.stageRatio );
            _this.stageElem.style.height = _this.stageHeight + 'px';
        }

        _this.tileWidth = ~~( _this.stageWidth / _this.cols );
        _this.tileHeight = ~~( _this.stageHeight / _this.rows );
        _this.dimAvg = ( _this.activeWidth + _this.activeHeight ) / 2;
        _this.spacing = Math.max( 1, ~~( _this.dimAvg * 0.0025 ) );

        _this.stageElem.style.marginTop = ( -_this.stageElem.offsetHeight / 2 ) + _this.heighteaderHeight / 2 + 'px';

        _this.boardTiles.each( 'updateDimensions' );
        _this.snake !== undefined && _this.snake.updateDimensions();
        _this.food !== undefined && _this.food.updateDimensions();
    };

    StatePlay.prototype.createBoardTiles = function() {
        for(let y = 0; y < this.rows; y++ ) {
            for(let x = 0; x < this.cols; x++ ) {
                this.boardTiles.add( new game.BoardTile({
                    parentState: this,
                    parentGroup: this.boardTiles,
                    col: x,
                    row: y,
                    x: x * this.tileWidth,
                    y: y * this.tileHeight,
                    w: this.tileWidth - this.spacing,
                    h: this.tileHeight - this.spacing
                }));
            }
        }
    };

    StatePlay.prototype.upOn = function() { game.currentState().keys.up = 1; }
    StatePlay.prototype.downOn = function() { game.currentState().keys.down = 1; }
    StatePlay.prototype.rightOn = function() { game.currentState().keys.right = 1; }
    StatePlay.prototype.leftOn = function() { game.currentState().keys.left = 1; }
    StatePlay.prototype.upOff = function() { game.currentState().keys.up = 0; }
    StatePlay.prototype.downOff = function() { game.currentState().keys.down = 0; }
    StatePlay.prototype.rightOff = function() { game.currentState().keys.right = 0; }
    StatePlay.prototype.leftOff = function() { game.currentState().keys.left = 0; }

    StatePlay.prototype.keydown = function(e) {
        e.preventDefault();
        const event = (e.keyCode ? e.keyCode : e.which),
            _this = game.currentState();
        if(event === 38 ||event === 87 ) { _this.upOn(); }
        if(event === 39 ||event === 68 ) { _this.rightOn(); }
        if(event === 40 ||event === 83 ) { _this.downOn(); }
        if(event === 37 ||event === 65 ) { _this.leftOn(); }
    };

    StatePlay.prototype.bindEvents = function() {
        const _this = game.currentState();
        window.addEventListener( 'keydown', _this.keydown, false );
        window.addEventListener( 'resize', _this.resize, false );
    };

    StatePlay.prototype.step = function() {
        this.boardTiles.each( 'update' );
        this.boardTiles.each( 'render' );
        this.snake.update();
        this.snake.render();
        this.food.update();
        this.food.render();
        this.time.update();
    };

    StatePlay.prototype.exit = function() {
        window.removeEventListener( 'keydown', this.keydown, false );
        window.removeEventListener( 'resize', this.resize, false );
        this.stageElem.innerHTML = '';
        this.grid.tiles = null;
        this.time = null;
    };

    game.addState( new StatePlay() );

})();

/* Game */

(function(){ 'use strict';
    game.config = {
        title: 'Snake',
        debug: window.location.hash === '#debug' ? 1 : 0,
        state: 'play'
    };
    game.setState( game.config.state );
    game.time = new game.Time();
    game.step = function() {
        requestAnimationFrame( game.step );
        game.states[ game.state ].step();
        game.time.update();
    };
    window.addEventListener( 'load', game.step, false );
})();
