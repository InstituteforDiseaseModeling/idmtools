FROM archlinux:latest

RUN pacman -Syy && pacman -S --noconfirm python openmpi snappy