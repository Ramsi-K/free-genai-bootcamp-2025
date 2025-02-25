class SceneMain extends Phaser.Scene {
	constructor() {
		super('SceneMain');
	}	

	preload() {
		this.load.image('bg', './bg.png');
		this.load.spritesheet('skyline', './skyline-og.png', { frameWidth: 32, frameHeight: 192 });

		this.sound_files = []
    Data.words.forEach(data => {
			const en = data.english.replace(/ /g,'_')
			const jp = data.romaji
			this.sound_files.push(en)
			this.sound_files.push(jp)
			this.load.audio(en, `audio/en/${en}.mp3`);
			this.load.audio(jp, `audio/jp/${jp}.mp3`);
    });

	}

	create() {
		const missing_sounds = this.sound_files.filter(sound => 
			!this.cache.audio.exists(sound)
		);

		if (missing_sounds.length > 0){
			console.error('Sounds are missing', missing_sounds)
			this.missing_text = this.add.text(32, 24, `Sounds are missing... ${missing_sounds.join(', ')}`, {
				font: '16px Arial',
				fill: '#ffffff'
			}).setOrigin(0);			

			throw "Sounds are missing..."
		}

		// This scene has two modes
		// falling: words are falling
		// correction: a popup after a word has hit where you hear the word and you must type the word.
		this.mode = 'falling'

		this.add.image(0, 0, 'bg').setOrigin(0,0)

		this.info_bar = new InfoBar(this)

		this.skyline = []
		for (let i = 0; i < 40; i++) {
			this.skyline.push(new SkylineBlock(this,i))
		}

		this.userText = this.add.text(this.game.config.width / 2, this.game.config.height / 2, '', {
			font: '40px Arial',
			fill: '#434343'
		}).setOrigin(0.5);

		this.word_manager = new WordManager(this)

		this.userInput = '';
		this.missle = new Missle(this);
		this.show_romaji = false

		this.word_manager.spawn()


		this.correction_box = new CorrectionBox(this)

		// Enable keyboard input
		this.input.keyboard.on('keydown', (event) => {
			if (this.mode === 'falling'){
				this.falling_input(event)
			} else if (this.mode === 'correction') {
				this.correction_box.input(event)
			}
		});
	} // create

	falling_input(ev){
		if  (ev.key === 'Dead') {
			// Ignore the 'Dead' key event
			return;
		} else if (ev.key === 'Shift') {
			this.userInput = ''
		} else if (ev.key === 'q') {
			this.scene.start('SceneReview')
		} else if (ev.keyCode === 8 && this.userInput.length > 0) {
			// Handle backspace
			this.userInput = this.userInput.slice(0, -1);
		} else if (ev.key === 'Enter') {
			this.fire()
			return;
		} else if ((ev.keyCode >= 65 && ev.keyCode <= 90) || ev.keyCode === 32) {
			// Add character for letters and space
			this.userInput += ev.key.toLowerCase();
		}
		this.userText.setText(this.userInput);
	}

	update() {
		this.info_bar.update()
		if (this.mode === 'falling') {
			this.word_manager.update()
			this.missle.update()
		} else if (this.mode === 'correction') {
			this.correction_box.update()
		}
	} // update

	addSpawnTimer(delay){
		this.timer = this.time.addEvent({
			delay: delay,
			callback: this.word_manager.spawn,
			callbackScope: this.word_manager
		})
	}

	showRomaji(){
		return this.show_romaji
	}

	fire(){
    let highestTarget = null;
    let maxY = -Infinity;

    this.word_manager.words.forEach((word) => {
        if (word.valid_target(this.userInput)) {
            if (word.y > maxY) {
                highestTarget = word;
                maxY = word.y;
            }
        }
    });

    if (highestTarget) {
        this.userInput = '';
        this.userText.setText(this.userInput);
        this.missle.fire(highestTarget.x_middle(), highestTarget);
    }
	} // fire



	hit(kanji_len,pos){
		for (let i = 0; i < kanji_len; i++) {
			this.skyline[pos+i].remove()
		}
	}
}