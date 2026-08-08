"""Config module that handles parsing and exposing server configuration"""
import yaml
from dataclasses import dataclass
from argparse import Namespace, ArgumentParser


# global config constant that is set up to current config after set_config() is called
CONFIG = None

def _parse_args() -> tuple[Namespace, list[str]]:
    """Parses command line config arguments"""
    
    parser = ArgumentParser()

    parser.add_argument('--config', '-c')
    parser.add_argument('--base_dir')
    parser.add_argument('--logfile')
    args, _ = parser.parse_known_args()
    return args

@dataclass(frozen=True)
class Config:
    """Read Only Dataclass that holds defines possible configuration"""
    
    config: str = "config.yaml"
    base_dir : str = "public"
    port : int = 65432
    host : str = "127.0.0.1"
    logfile : str = "logs"
    
    def __str__(self):
        #return "".join(f"{k} {v}" for k,v in dir(__class__)) + "\n"
        return "config: " + self.config + ", base_dir: " + self.base_dir + ", logfile: " + self.logfile
        
    
def set_config() -> None:  
    """Sets up config, gives precedence to cmd arguments over config file"""
      
    global CONFIG
    
    parsed_kwargs : Namespace = _parse_args()
    
    kwargs_dict : dict = {}
    
    for kwarg in parsed_kwargs._get_kwargs():
        if kwarg[1] is not None:
            kwargs_dict[kwarg[0]] = kwarg[1]    
    
    if kwargs_dict.get("config"):
        config_file : str = kwargs_dict["config"]
    else:
        config_file = "config.yaml"
    
    with open(config_file) as f:
        c : dict = yaml.safe_load(f)

        if c:
            c.update(kwargs_dict)
                    
            CONFIG = Config(**c)
        else:
            CONFIG = Config(**kwargs_dict)
            
