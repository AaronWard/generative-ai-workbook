

## MFLux WebUI

- https://github.com/CharafChnioune/MFLUX-WEBUI - so far this is the only Web UI that is made for MLFUX which is remains up to date

```
git clone https://github.com/CharafChnioune/mflux-webui.git
cd mflux-webui
conda create -n mflux python=3.12
conda activate mflux
pip install -r requirements.txt
```



-  http://127.0.0.1:7860


---

Environment vars:

```
export LORA_LIBRARY_PATH="/path/to/your/lora/models"  # Custom LoRA library location
export MFLUX_CONFIG_PATH="/path/to/config/files"     # Custom config directory
export MFLUX_BATTERY_MONITOR=true                    # Enable battery monitoring by default
```