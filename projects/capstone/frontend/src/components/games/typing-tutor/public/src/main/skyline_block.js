class SkylineBlock {
	constructor(scene,index) {
		this.hit = false
		this.scene = scene
		this.index = index
		const x = index*32
		this.height = 192
		const y = this.scene.game.config.height - this.height - this.scene.info_bar.height
		this.sprite = scene.add.sprite(x, y, 'skyline', index);
		this.sprite.setOrigin(0,0)
	}

	remove(){
		this.hit = true
		this.sprite.visible = false
	}
}