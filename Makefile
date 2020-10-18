.PHONY: install

sources := $(wildcard birdthing/*)
data := $(wildcard birdthing/data/*)

dist/birdthing-0.1.0.tar.gz: $(sources) $(data)
	poetry build

install: dist/birdthing-0.1.0.tar.gz birdthing.service
	pip3 install dist/birdthing-0.1.0.tar.gz
	cp birdthing.service ~/.config/systemd/user/birdthing.service
	systemctl --user daemon-reload
	systemctl --user enable --now birdthing
	# sudo loginctl enable-linger $(USER) # Optional
