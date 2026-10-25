# Maintainer: pyro pik
pkgname=crosshair-rs
pkgver=0.1.0
pkgrel=4
pkgdesc="Tiny click-through always-on-top crosshair overlay for X11 (Rust port of fullscreen-crosshair)"
arch=('x86_64')
url="https://github.com/Pyrotik/fullscreen-crosshair"
license=('MIT')
depends=('glibc' 'gcc-libs')            # that's all: no Qt, no GTK, no GL
optdepends=('picom: compositor for true opacity (without one the crosshair is drawn as a shaped, fully opaque window)')
makedepends=('cargo')
source=("fullscreen-crosshair-rs.tar.gz")   # tarball of this directory (contains fullscreen-crosshair-rs/)
sha256sums=('SKIP')

prepare() {
  cd fullscreen-crosshair-rs
  cargo fetch --locked --target "$CARCH-unknown-linux-gnu"
}

build() {
  cd fullscreen-crosshair-rs
  export RUSTUP_TOOLCHAIN=stable CARGO_TARGET_DIR=target
  cargo build --release --frozen
}

check() {
  cd fullscreen-crosshair-rs
  export RUSTUP_TOOLCHAIN=stable
  ./target/release/crosshair-rs --help >/dev/null
}

package() {
  cd fullscreen-crosshair-rs
  install -Dm755 target/release/crosshair-rs "$pkgdir/usr/bin/crosshair-rs"
  install -Dm644 crosshair-rs.desktop "$pkgdir/usr/share/applications/crosshair-rs.desktop"
  install -Dm644 assets/crosshair-rs.svg "$pkgdir/usr/share/icons/hicolor/scalable/apps/crosshair-rs.svg"
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
  install -Dm644 assets/DejaVu-LICENSE.txt "$pkgdir/usr/share/licenses/$pkgname/DejaVu-LICENSE.txt"
}
