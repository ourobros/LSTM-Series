from trainer import Trainer
from utils import *

def main():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    trainer = Trainer(config)
    trainer.train()
    checkpoint = trainer.get_checkpoint_name()
    save_predictions(checkpoint=checkpoint, config=config)


if __name__ == '__main__':
    main()