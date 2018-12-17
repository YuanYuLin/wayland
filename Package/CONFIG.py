import ops
import iopc

TARBALL_FILE="wayland-1.15.0.tar.xz"
TARBALL_DIR="wayland-1.15.0"
INSTALL_DIR="wayland-bin"
pkg_path = ""
output_dir = ""
tarball_pkg = ""
tarball_dir = ""
install_dir = ""
install_tmp_dir = ""
cc_host = ""
tmp_include_dir = ""
dst_include_dir = ""
dst_lib_dir = ""

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global install_tmp_dir
    global tarball_dir
    global cc_host
    global tmp_include_dir
    global dst_include_dir
    global dst_lib_dir
    global src_pkgconfig_dir
    global dst_pkgconfig_dir
    global host_utils
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    install_tmp_dir = ops.path_join(output_dir, INSTALL_DIR + "-tmp")
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    cc_host_str = ops.getEnv("CROSS_COMPILE")
    cc_host = cc_host_str[:len(cc_host_str) - 1]
    tmp_include_dir = ops.path_join(output_dir, ops.path_join("include",args["pkg_name"]))
    dst_include_dir = ops.path_join("include",args["pkg_name"])
    dst_lib_dir = ops.path_join(install_dir, "lib")
    src_pkgconfig_dir = ops.path_join(pkg_path, "pkgconfig")
    dst_pkgconfig_dir = ops.path_join(install_dir, "pkgconfig")
    host_utils = ops.path_join(iopc.getSdkPath(), "host_utils")

def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    ops.exportEnv(ops.setEnv("CXX", ops.getEnv("CROSS_COMPILE") + "g++"))
    ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    ops.exportEnv(ops.setEnv("DESTDIR", install_tmp_dir))
    #ops.exportEnv(ops.setEnv("PKG_CONFIG_LIBDIR", ops.path_join(iopc.getSdkPath(), "pkgconfig")))
    #ops.exportEnv(ops.setEnv("PKG_CONFIG_SYSROOT_DIR", iopc.getSdkPath()))
    #ops.exportEnv(ops.setEnv("WAYLAND_SCANNER_UTIL", wayland_scanner))
    ops.exportEnv(ops.addEnv("PATH", ops.path_join(pkg_path, "host_utils")))

    return False

def MAIN_EXTRACT(args):
    set_global(args)

    ops.unTarXz(tarball_pkg, output_dir)
    #ops.copyto(ops.path_join(pkg_path, "finit.conf"), output_dir)

    return True

def MAIN_PATCH(args, patch_group_name):
    set_global(args)
    for patch in iopc.get_patch_list(pkg_path, patch_group_name):
        if iopc.apply_patch(tarball_dir, patch):
            continue
        else:
            sys.exit(1)

    return True

def MAIN_CONFIGURE(args):
    set_global(args)

    cflags = iopc.get_includes()
    libs = iopc.get_libs()

    extra_conf = []
    extra_conf.append("--host=" + cc_host)
    extra_conf.append("--disable-silent-rules")
    extra_conf.append("--with-host-scanner")
    extra_conf.append("--disable-documentation")
    extra_conf.append('FFI_CFLAGS=' + cflags)
    extra_conf.append('FFI_LIBS=' + libs)
    extra_conf.append('EXPAT_CFLAGS=' + cflags)
    extra_conf.append('EXPAT_LIBS=' + libs)
    extra_conf.append('LIBXML_CFLAGS=' + cflags)
    extra_conf.append('LIBXML_LIBS=' + libs)
    iopc.configure(tarball_dir, extra_conf)

    return True

def MAIN_BUILD(args):
    set_global(args)

    print "AAAA" + ops.getEnv("PATH")
    ops.mkdir(install_dir)
    ops.mkdir(install_tmp_dir)
    iopc.make(tarball_dir)
    iopc.make_install(tarball_dir)

    ops.mkdir(install_dir)
    ops.mkdir(dst_lib_dir)
    libwayland_client = "libwayland-client.so.0.3.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libwayland_client), dst_lib_dir)
    ops.ln(dst_lib_dir, libwayland_client, "libwayland-client.so.0.3")
    ops.ln(dst_lib_dir, libwayland_client, "libwayland-client.so.0")
    ops.ln(dst_lib_dir, libwayland_client, "libwayland-client.so")

    libwayland_cursor = "libwayland-cursor.so.0.0.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libwayland_cursor), dst_lib_dir)
    ops.ln(dst_lib_dir, libwayland_cursor, "libwayland-cursor.so.0.0")
    ops.ln(dst_lib_dir, libwayland_cursor, "libwayland-cursor.so.0")
    ops.ln(dst_lib_dir, libwayland_cursor, "libwayland-cursor.so")

    libwayland_egl = "libwayland-egl.so.1.0.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libwayland_egl), dst_lib_dir)
    ops.ln(dst_lib_dir, libwayland_egl, "libwayland-egl.so.1.0")
    ops.ln(dst_lib_dir, libwayland_egl, "libwayland-egl.so.1")
    ops.ln(dst_lib_dir, libwayland_egl, "libwayland-egl.so")

    libwayland_server = "libwayland-server.so.0.1.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libwayland_server), dst_lib_dir)
    ops.ln(dst_lib_dir, libwayland_server, "libwayland-server.so.0.1")
    ops.ln(dst_lib_dir, libwayland_server, "libwayland-server.so.0")
    ops.ln(dst_lib_dir, libwayland_server, "libwayland-server.so")

    ops.mkdir(tmp_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/."), tmp_include_dir)

    ops.mkdir(host_utils)
    ops.copyto(ops.path_join(pkg_path, "host_utils/wayland-scanner"), host_utils)

    ops.mkdir(dst_pkgconfig_dir)
    ops.copyto(ops.path_join(src_pkgconfig_dir, '.'), dst_pkgconfig_dir)
    return False

def MAIN_INSTALL(args):
    set_global(args)

    iopc.installBin(args["pkg_name"], ops.path_join(ops.path_join(install_dir, "lib"), "."), "lib")
    iopc.installBin(args["pkg_name"], ops.path_join(tmp_include_dir, "."), dst_include_dir)
    iopc.installBin(args["pkg_name"], ops.path_join(dst_pkgconfig_dir, '.'), "pkgconfig")

    return False

def MAIN_SDKENV(args):
    set_global(args)

    cflags = ""
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/' + args["pkg_name"])
    iopc.add_includes(cflags)

    libs = ""
    libs += " -lwayland-client -lwayland-cursor -lwayland-egl -lwayland-server"
    iopc.add_libs(libs)

    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

