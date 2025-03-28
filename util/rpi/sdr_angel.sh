#!/bin/bash
#
# Script to auto build and install SDR Andgel for pi.
#
# Run this script With curl:
# bash <(curl -sL https://gist.githubusercontent.com/TopherTimeMachine/e111dc2ba32ade354812005aff9d7dc7/raw/248da8a86018e7a55f970902c284952c16fb26b7/sdrangel_pi.sh) 
#
# based on Symbilote's yt video https://www.youtube.com/watch?v=jBmwiwNyqbI
# and script based on https://github.com/f4exb/sdrangel/wiki/Compile-from-source-in-Linux
#

# Exit on error
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if user has sudo privileges
check_sudo() {
    if ! sudo -v; then
        echo "Error: This script requires sudo privileges"
        exit 1
    fi
}

# Function to cleanup on exit
cleanup() {
    echo "Cleaning up..."
    # Add cleanup commands here
    exit 0
}

# Set up trap for cleanup
trap cleanup EXIT

# Function to install Airspy
install_airspy() {
    echo "Installing Airspy..."
    if ! cd /opt/build; then
        echo "Error: Could not change to /opt/build directory"
        return 1
    fi
    
    if ! git clone https://github.com/airspy/airspyone_host.git libairspy; then
        echo "Error: Failed to clone Airspy repository"
        return 1
    fi
    
    cd libairspy
    git reset --hard 37c768ce9997b32e7328eb48972a7fda0a1f8554
    mkdir -p build && cd build
    
    if ! cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/libairspy ..; then
        echo "Error: CMake configuration failed for Airspy"
        return 1
    fi
    
    if ! make -j $(nproc) install; then
        echo "Error: Build failed for Airspy"
        return 1
    fi
}

# Function to install SDRplay RSP1
install_sdrplay_rsp1() {
    echo "Installing SDRplay RSP1..."
    cd /opt/build
    git clone https://github.com/f4exb/libmirisdr-4.git
    cd libmirisdr-4
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/libmirisdr ..
    make -j $(nproc) install
}

# Function to install SDRplay V3
install_sdrplay_v3() {
    echo "Installing SDRplay V3..."
    cd /opt/build
    git clone https://github.com/srcejon/sdrplayapi.git
    cd sdrplayapi
    sudo ./install_lib.sh
}

# Function to install RTL-SDR
install_rtlsdr() {
    echo "Installing RTL-SDR..."
    cd /opt/build
    
    # Remove existing directory if it exists
    if [ -d "librtlsdr" ]; then
        echo "Removing existing librtlsdr directory..."
        rm -rf librtlsdr
    fi
    
    git clone https://github.com/osmocom/rtl-sdr.git librtlsdr
    cd librtlsdr
    git reset --hard 420086af84d7eaaf98ff948cd11fea2cae71734a 
    mkdir build; cd build
    cmake -Wno-dev -DDETACH_KERNEL_DRIVER=ON -DCMAKE_INSTALL_PREFIX=/opt/install/librtlsdr ..
    make -j $(nproc) install
}

# Function to install Pluto SDR
install_pluto_sdr() {
    echo "Installing Pluto SDR..."
    cd /opt/build
    git clone https://github.com/analogdevicesinc/libiio.git
    cd libiio
    git reset --hard v0.21
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/libiio -DINSTALL_UDEV_RULE=OFF ..
    make -j $(nproc) install
}

# Function to install BladeRF
install_bladerf() {
    echo "Installing BladeRF..."
    cd /opt/build
    git clone https://github.com/Nuand/bladeRF.git
    cd bladeRF/host
    git reset --hard "2023.02"
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/libbladeRF -DINSTALL_UDEV_RULES=OFF ..
    make -j $(nproc) install
}

# Function to install HackRF
install_hackrf() {
    echo "Installing HackRF..."
    cd /opt/build
    git clone https://github.com/greatscottgadgets/hackrf.git
    cd hackrf/host
    git reset --hard "v2024.02.1"
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/libhackrf -DINSTALL_UDEV_RULES=OFF ..
    make -j $(nproc) install
}

# Function to install LimeSDR
install_limesdr() {
    echo "Installing LimeSDR..."
    cd /opt/build
    git clone https://github.com/myriadrf/LimeSuite.git
    cd LimeSuite
    git reset --hard "v20.01.0"
    mkdir builddir; cd builddir
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/LimeSuite ..
    make -j $(nproc) install
}

# Function to install AirspyHF
install_airspyhf() {
    echo "Installing AirspyHF..."
    cd /opt/build
    git clone https://github.com/airspy/airspyhf
    cd airspyhf
    git reset --hard 1af81c0ca18944b8c9897c3c98dc0a991815b686
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/libairspyhf ..
    make -j $(nproc) install
}

# Function to install Perseus
install_perseus() {
    echo "Installing Perseus..."
    cd /opt/build
    git clone https://github.com/f4exb/libperseus-sdr.git
    cd libperseus-sdr
    git checkout fixes
    git reset --hard afefa23e3140ac79d845acb68cf0beeb86d09028
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/libperseus ..
    make -j $(nproc)
    make install
}

# Function to install dependencies
install_dependencies() {
    # Check if required directories exist
    if [ ! -d "/opt/build" ]; then
        sudo mkdir -p /opt/build
        sudo chown $USER:users /opt/build
    fi
    
    if [ ! -d "/opt/install" ]; then
        sudo mkdir -p /opt/install
        sudo chown $USER:users /opt/install
    fi

    # Check if required packages are installed
    local required_packages=(
        "rtl-sdr"
        "cmake"
        "git"
        "g++"
        "pkg-config"
        "autoconf"
        "automake"
        "libtool"
        "libfftw3-dev"
        "libusb-1.0-0-dev"
        "libusb-dev"
        "libhidapi-dev"
        "libopengl-dev"
        "qtbase5-dev"
        "qtchooser"
        "libqt5multimedia5-plugins"
        "qtmultimedia5-dev"
        "libqt5websockets5-dev"
        "qttools5-dev"
        "qttools5-dev-tools"
        "libqt5opengl5-dev"
        "libqt5quick5"
        "libqt5charts5-dev"
        "qml-module-qtlocation"
        "qml-module-qtpositioning"
        "qml-module-qtquick-window2"
        "qml-module-qtquick-dialogs"
        "qml-module-qtquick-controls"
        "qml-module-qtquick-controls2"
        "qml-module-qtquick-layouts"
        "libqt5serialport5-dev"
        "qtdeclarative5-dev"
        "qtpositioning5-dev"
        "qtlocation5-dev"
        "libqt5texttospeech5-dev"
        "qtwebengine5-dev"
        "qtbase5-private-dev"
        "libqt5gamepad5-dev"
        "libqt5svg5-dev"
        "libfaad-dev"
        "libflac-dev"
        "zlib1g-dev"
        "libboost-all-dev"
        "libasound2-dev"
        "pulseaudio"
        "libopencv-dev"
        "libxml2-dev"
        "bison"
        "flex"
        "ffmpeg"
        "libavcodec-dev"
        "libavformat-dev"
        "libopus-dev"
        "doxygen"
        "graphviz"
    )

    echo "Checking and installing required packages..."
    for package in "${required_packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            echo "Installing $package..."
            if ! sudo apt-get install -y "$package"; then
                echo "Error: Failed to install $package"
                return 1
            fi
        fi
    done

    # APT
    # Optionally: sudo apt-get install libsndfile-dev
    cd /opt/build
    git clone https://github.com/srcejon/aptdec.git
    cd aptdec
    git checkout libaptdec
    git submodule update --init --recursive
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/aptdec ..
    make -j $(nproc) install

    #CM265cc
    echo "Installing CM256cc..."
    cd /opt/build
    git clone https://github.com/f4exb/cm256cc.git
    cd cm256cc
    git reset --hard 6f4a51802f5f302577d6d270a9fc0cb7a1ee28ef
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/cm256cc ..
    make -j $(nproc) install

    # libDAB
    echo "Installing libDAB..."
    cd /opt/build
    git clone https://github.com/srcejon/dab-cmdline
    cd dab-cmdline/library
    git checkout msvc
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/libdab ..
    make -j $(nproc) install

    #MBElib
    echo "Installing MBElib..."
    cd /opt/build
    git clone https://github.com/szechyjs/mbelib.git
    cd mbelib
    git reset --hard 9a04ed5c78176a9965f3d43f7aa1b1f5330e771f
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/mbelib ..
    make -j $(nproc) install

    #SerialDV
    echo "Installing SerialDV..."
    cd /opt/build
    git clone https://github.com/f4exb/serialDV.git
    cd serialDV
    git reset --hard "v1.1.4"
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/serialdv ..
    make -j $(nproc) install

    # DSDcc
    echo "Installing DSDcc..."
    cd /opt/build
    git clone https://github.com/f4exb/dsdcc.git
    cd dsdcc
    git reset --hard "v1.9.5"
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/dsdcc -DUSE_MBELIB=ON -DLIBMBE_INCLUDE_DIR=/opt/install/mbelib/include -DLIBMBE_LIBRARY=/opt/install/mbelib/lib/libmbe.so -DLIBSERIALDV_INCLUDE_DIR=/opt/install/serialdv/include/serialdv -DLIBSERIALDV_LIBRARY=/opt/install/serialdv/lib/libserialdv.so ..
    make -j $(nproc) install

    #Codec2/FreeDV
    echo "Installing Codec2/FreeDV..."
    sudo apt-get -y install libspeexdsp-dev libsamplerate0-dev
    cd /opt/build
    git clone https://github.com/drowe67/codec2-dev.git codec2
    cd codec2
    git reset --hard "v1.0.3"
    mkdir build_linux; cd build_linux
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/codec2 ..
    make -j $(nproc) install

    #SGP4
    echo "Installing SGP4..."
    cd /opt/build
    git clone https://github.com/dnwrnr/sgp4.git
    cd sgp4
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/sgp4 ..
    make -j $(nproc) install

    # LibSigMF
    echo "Installing LibSigMF..."
    cd /opt/build
    git clone https://github.com/f4exb/libsigmf.git
    cd libsigmf
    git checkout "new-namespaces"
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/libsigmf .. 
    make -j $(nproc) install

    #GGMorse
    echo "Installing GGMorse..."
    cd /opt/build
    git clone https://github.com/ggerganov/ggmorse.git
    cd ggmorse
    mkdir build; cd build
    cmake -Wno-dev -DCMAKE_INSTALL_PREFIX=/opt/install/ggmorse -DGGMORSE_BUILD_TESTS=OFF -DGGMORSE_BUILD_EXAMPLES=OFF ..
    make -j $(nproc) install
}

# Main script execution
main() {
    # Check for sudo privileges
    check_sudo

    # Check if dialog is installed
    if ! command_exists dialog; then
        echo "Installing dialog..."
        if ! sudo apt-get update || ! sudo apt-get install -y dialog; then
            echo "Error: Failed to install dialog"
            exit 1
        fi
    fi

    # Show the hardware selection menu
    if ! dialog --title "SDR Angel Install for RasPi" \
            --checklist "Select hardware to install:" 20 60 10 \
            "airspy" "Airspy" OFF \
            "sdrplay_rsp1" "SDRplay RSP1" OFF \
            "sdrplay_v3" "SDRplay V3" OFF \
            "rtlsdr" "RTL-SDR" OFF \
            "pluto_sdr" "Pluto SDR" OFF \
            "bladerf" "BladeRF" OFF \
            "hackrf" "HackRF" OFF \
            "limesdr" "LimeSDR" OFF \
            "airspyhf" "AirspyHF" OFF \
            "perseus" "Perseus" OFF 2>/tmp/hardware_choices; then
        echo "Error: Dialog menu failed"
        exit 1
    fi

    # Install dependencies
    if ! install_dependencies; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi

    # Process hardware choices
    if [ -f "/tmp/hardware_choices" ]; then
        choices=$(cat /tmp/hardware_choices)
        for choice in $choices; do
            case $choice in
                "airspy") install_airspy ;;
                "sdrplay_rsp1") install_sdrplay_rsp1 ;;
                "sdrplay_v3") install_sdrplay_v3 ;;
                "rtlsdr") install_rtlsdr ;;
                "pluto_sdr") install_pluto_sdr ;;
                "bladerf") install_bladerf ;;
                "hackrf") install_hackrf ;;
                "limesdr") install_limesdr ;;
                "airspyhf") install_airspyhf ;;
                "perseus") install_perseus ;;
            esac
        done
    fi

    # Build SDRangel if not already installed
    if [ ! -f "/opt/install/sdrangel/bin/sdrangel" ]; then
        echo "Building SDRangel..."
        cd /opt/build
        
        # Remove existing sdrangel directory if it exists
        if [ -d "sdrangel" ]; then
            rm -rf sdrangel
        fi
        
        git clone https://github.com/f4exb/sdrangel.git
        cd sdrangel
        mkdir build; cd build
        cmake -Wno-dev -DDEBUG_OUTPUT=ON -DRX_SAMPLE_24BIT=ON \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        -DMIRISDR_DIR=/opt/install/libmirisdr \
        -DAIRSPY_DIR=/opt/install/libairspy \
        -DAIRSPYHF_DIR=/opt/install/libairspyhf \
        -DBLADERF_DIR=/opt/install/libbladeRF \
        -DHACKRF_DIR=/opt/install/libhackrf \
        -DRTLSDR_DIR=/opt/install/librtlsdr \
        -DLIMESUITE_DIR=/opt/install/LimeSuite \
        -DIIO_DIR=/opt/install/libiio \
        -DPERSEUS_DIR=/opt/install/libperseus \
        -DXTRX_DIR=/opt/install/xtrx-images \
        -DSOAPYSDR_DIR=/opt/install/SoapySDR \
        -DUHD_DIR=/opt/install/uhd \
        -DAPT_DIR=/opt/install/aptdec \
        -DCM256CC_DIR=/opt/install/cm256cc \
        -DDSDCC_DIR=/opt/install/dsdcc \
        -DSERIALDV_DIR=/opt/install/serialdv \
        -DMBE_DIR=/opt/install/mbelib \
        -DCODEC2_DIR=/opt/install/codec2 \
        -DSGP4_DIR=/opt/install/sgp4 \
        -DLIBSIGMF_DIR=/opt/install/libsigmf \
        -DDAB_DIR=/opt/install/libdab \
        -DGGMORSE_DIR=/opt/install/ggmorse \
        -DCMAKE_INSTALL_PREFIX=/opt/install/sdrangel ..
        make -j $(nproc) install
    fi

    # Create desktop entry only if SDRangel is successfully installed
    if [ -f "/opt/install/sdrangel/bin/sdrangel" ]; then
        # Create the desktop entry file
        echo "Creating desktop entry for SDRangel..."
        cat << 'EOF' | sudo tee /usr/share/applications/sdrangel.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=SDRangel
Comment=Software-Defined Radio Software
Exec=/opt/install/sdrangel/bin/sdrangel
Icon=/opt/install/sdrangel/share/icons/hicolor/48x48/apps/sdrangel.png
Terminal=false
Categories=HamRadio;Science;Qt;
EOF

        # Make the desktop entry executable
        sudo chmod +x /usr/share/applications/sdrangel.desktop
        echo "Desktop entry created successfully!"

        # Run SDRangel
        echo "Starting SDRangel..."
        /opt/install/sdrangel/bin/sdrangel
    else
        echo "Error: SDRangel installation failed. Please check the build logs for errors."
        exit 1
    fi
}

# Run the main function
main
