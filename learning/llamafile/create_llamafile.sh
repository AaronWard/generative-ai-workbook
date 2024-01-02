#!/bin/bash

# Function to install cosmocc if not already installed
install_cosmocc() { /Users/award40/Desktop/cosmocc/bin/make
    if [ ! -d "/Users/award40/Desktop/cosmocc/" ]; then
        echo "Installing Cosmopolitan Libc..."
        mkdir -p /Users/award40/Desktop/cosmocc
        curl -o /Users/award40/Desktop/cosmocc/cosmocc.zip -L https://cosmo.zip/pub/cosmocc/cosmocc.zip
        unzip /Users/award40/Desktop/cosmocc/cosmocc.zip
    else
        echo "Cosmopolitan Libc already installed."
    fi
}

# Function to create llamafile executable from a .gguf file
create_llamafile() {
    gguf_file=$1
    llamafile_name=$(basename "$gguf_file" .gguf).llamafile

    echo "Creating llamafile executable: $llamafile_name from $gguf_file"
    /Users/award40/Desktop/cosmocc/bin/make -j8
    sudo /Users/award40/Desktop/cosmocc/bin/make install PREFIX=/usr/local
    cp /usr/local/bin/llamafile "$llamafile_name"
    chmod +x "$llamafile_name"
    zipalign -j0 "$llamafile_name" "$gguf_file" .args
    echo "Executable created: $llamafile_name"
}

# Main script
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 path/to/model.gguf"
    exit 1
fi

gguf_file=$1

install_cosmocc
create_llamafile "$gguf_file"
