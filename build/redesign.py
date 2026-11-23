# Apply the Fanoos desktop experience to the pinned RustDesk source.
# Every transformation is guarded so an upstream source change fails the build
# instead of silently producing a partially-branded client.
from pathlib import Path
from defaults import render_defaults


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    Path(path).write_text(render_defaults(content), encoding="utf-8")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if old not in content:
        raise RuntimeError(f"Fanoos redesign patch point not found: {label}")
    return content.replace(old, new, 1)


# Persian is the product default, while explicit user language choices win.
lang_path = "src/lang.rs"
s = read(lang_path)
needle = '    let mut lang = saved_lang.to_lowercase();\n'
replacement = '''    let mut lang = saved_lang.to_lowercase();
    // Fanoos Desk is a Persian-first client. Keep an explicit user choice,
    // but use Persian when no language has been selected yet.
    if lang.is_empty() || lang == "default" {
        lang = "fa".to_owned();
    }
'''
s = replace_once(s, needle, replacement, "Persian default language")
write(lang_path, s)


# Synchronize Flutter's locale with RustDesk's selected language. This gives
# Persian/Arabic/Hebrew/Urdu real RTL layout instead of translated LTR text.
main_path = "flutter/lib/main.dart"
s = read(main_path)
helper = r'''
Locale _fanoosUiLocale() {
  var selected =
      bind.mainGetLocalOption(key: kCommConfKeyLang).trim().toLowerCase();
  if (selected.isEmpty || selected == 'default') {
    selected = 'fa';
  }
  switch (selected) {
    case 'zh-cn':
      return const Locale('zh', 'CN');
    case 'zh-tw':
      return const Locale('zh', 'TW');
    case 'pt-br':
      return const Locale('pt', 'BR');
    case 'pt-pt':
      return const Locale('pt', 'PT');
    default:
      return Locale(selected.split(RegExp('[-_]')).first);
  }
}

'''
s = replace_once(
    s,
    "void _runApp(\n",
    helper + "void _runApp(\n",
    "Flutter locale helper",
)
s = replace_once(
    s,
    "      themeMode: themeMode,\n      home: home,\n",
    "      themeMode: themeMode,\n      locale: _fanoosUiLocale(),\n      home: home,\n",
    "installer/app locale",
)
s = replace_once(
    s,
    "          themeMode: MyTheme.currentThemeMode(),\n          home: isDesktop\n",
    "          themeMode: MyTheme.currentThemeMode(),\n          locale: _fanoosUiLocale(),\n          home: isDesktop\n",
    "main app locale",
)
write(main_path, s)


# Prefill the Network/Server dialog with Fanoos's private server defaults.
# Users can still override these values manually if they need another server.
dialog_path = "flutter/lib/mobile/widgets/dialog.dart"
s = read(dialog_path)
dialog_old = """  final idCtrl = TextEditingController(text: serverConfig.idServer);
  final relayCtrl = TextEditingController(text: serverConfig.relayServer);
  final apiCtrl = TextEditingController(text: serverConfig.apiServer);
  final keyCtrl = TextEditingController(text: serverConfig.key);
"""
dialog_new = """  const fanoosDefaultServer = '__FANOOS_IP__';
  const fanoosDefaultKey =
      '__FANOOS_KEY__';
  final idCtrl = TextEditingController(
      text: serverConfig.idServer.trim().isEmpty
          ? fanoosDefaultServer
          : serverConfig.idServer);
  final relayCtrl = TextEditingController(
      text: serverConfig.relayServer.trim().isEmpty
          ? fanoosDefaultServer
          : serverConfig.relayServer);
  final apiCtrl = TextEditingController(text: serverConfig.apiServer);
  final keyCtrl = TextEditingController(
      text: serverConfig.key.trim().isEmpty
          ? fanoosDefaultKey
          : serverConfig.key);
"""
s = replace_once(
    s,
    dialog_old,
    dialog_new,
    "Network dialog Fanoos defaults",
)
write(dialog_path, s)


# Desktop home: responsive dashboard with visible server configuration.
home_path = "flutter/lib/desktop/pages/desktop_home_page.dart"
s = read(home_path)
import_line = "import 'package:flutter_hbb/models/platform_model.dart';\n"
s = replace_once(
    s,
    import_line,
    import_line + "import 'package:flutter_hbb/mobile/widgets/dialog.dart';\n",
    "server settings import",
)

build_start = s.index(
    "    return _buildBlock(",
    s.index("  Widget build(BuildContext context)"),
)
build_end = s.index("\n  Widget _buildBlock", build_start)

new_build = r'''    final isOutgoingOnly = bind.isOutgoingOnly();
    return _buildBlock(
      child: LayoutBuilder(
        builder: (context, constraints) {
          final theme = Theme.of(context);
          final dark = theme.brightness == Brightness.dark;
          final accent = const Color(0xFFAB390F);
          final accentSoft =
              dark ? const Color(0xFF4A2018) : const Color(0xFFFFF0CA);
          final canvas =
              dark ? const Color(0xFF0B1220) : const Color(0xFFFFF9EF);
          final surface =
              dark ? const Color(0xFF111C2D) : const Color(0xFFFFFFFF);
          final border =
              dark ? const Color(0xFF26364C) : const Color(0xFFDDE5E7);
          final muted =
              dark ? const Color(0xFF9FB0C4) : const Color(0xFF667781);

          Widget panel(Widget child, {EdgeInsetsGeometry? padding}) {
            return Container(
              padding: padding,
              clipBehavior: Clip.antiAlias,
              decoration: BoxDecoration(
                color: surface,
                borderRadius: BorderRadius.circular(22),
                border: Border.all(color: border),
                boxShadow: dark
                    ? const []
                    : const [
                        BoxShadow(
                          color: Color(0x12000000),
                          blurRadius: 24,
                          offset: Offset(0, 8),
                        ),
                      ],
              ),
              child: child,
            );
          }

          Widget serverCard() {
            return FutureBuilder<String>(
              future: bind.mainGetOptions(),
              builder: (context, snapshot) {
                var config = ServerConfig();
                if (snapshot.hasData) {
                  try {
                    config = ServerConfig.fromOptions(
                        jsonDecode(snapshot.data!) as Map<String, dynamic>);
                  } catch (_) {}
                }
                final hasCustomId = config.idServer.trim().isNotEmpty;
                final idServer = hasCustomId
                    ? config.idServer.trim()
                    : '__FANOOS_IP__';
                final relayServer = config.relayServer.trim().isNotEmpty
                    ? config.relayServer.trim()
                    : '__FANOOS_IP__';

                return Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: accentSoft,
                    borderRadius: BorderRadius.circular(18),
                    border: Border.all(color: accent.withOpacity(.22)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 42,
                            height: 42,
                            decoration: BoxDecoration(
                              color: accent.withOpacity(.12),
                              borderRadius: BorderRadius.circular(13),
                            ),
                            child: Icon(Icons.dns_rounded, color: accent),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  translate('ID/Relay Server'),
                                  style: const TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                const SizedBox(height: 3),
                                Text(
                                  idServer,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  textDirection: TextDirection.ltr,
                                  style: TextStyle(fontSize: 11.5, color: muted),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 9, vertical: 5),
                            decoration: BoxDecoration(
                              color: const Color(0xFFFFEDD5),
                              borderRadius: BorderRadius.circular(999),
                            ),
                            child: Text(
                              hasCustomId ? 'سفارشی' : 'پیش‌فرض',
                              style: TextStyle(
                                color: const Color(0xFF9A3412),
                                fontSize: 10.5,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ],
                      ),
                      ...[
                        const SizedBox(height: 12),
                        Text(
                          [
                            'Relay: $relayServer',
                            if (config.apiServer.trim().isNotEmpty)
                              'API: ${config.apiServer.trim()}',
                          ].join('   •   '),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          textDirection: TextDirection.ltr,
                          style: TextStyle(fontSize: 10.5, color: muted),
                        ),
                      ],
                      const SizedBox(height: 14),
                      SizedBox(
                        height: 40,
                        child: OutlinedButton.icon(
                          onPressed: bind.isDisableSettings()
                              ? null
                              : () => showServerSettings(
                                    gFFI.dialogManager,
                                    setState,
                                  ),
                          icon: const Icon(Icons.tune_rounded, size: 18),
                          label: Text(
                            hasCustomId
                                ? 'ویرایش تنظیمات سرور'
                                : 'تنظیمات سرور فانوس',
                          ),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: accent,
                            side: BorderSide(color: accent.withOpacity(.38)),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              },
            );
          }

          final localPanel = panel(
            SingleChildScrollView(
              controller: _leftPaneScrollController,
              padding: const EdgeInsets.all(18),
              child: Column(
                key: _childKey,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 46,
                        height: 46,
                        decoration: BoxDecoration(
                          color: accent.withOpacity(.12),
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: Icon(
                          Icons.computer_rounded,
                          color: accent,
                          size: 25,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              translate('Your Desktop'),
                              style: const TextStyle(
                                fontSize: 17,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            const SizedBox(height: 3),
                            Text(
                              'شناسه و دسترسی این دستگاه',
                              style: TextStyle(fontSize: 11.5, color: muted),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 18),
                  serverCard(),
                  if (!isOutgoingOnly) ...[
                    const SizedBox(height: 14),
                    buildPresetPasswordWarning(),
                    buildIDBoard(context),
                    buildPasswordBoard(context),
                  ],
                  const SizedBox(height: 8),
                  Divider(color: border),
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: OnlineStatusWidget(),
                  ),
                  Obx(() => buildHelpCards(stateGlobal.updateUrl.value)),
                ],
              ),
            ),
          );

          final remotePanel = panel(
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(18, 16, 18, 12),
                  child: Row(
                    children: [
                      Icon(
                        Icons.send_to_mobile_rounded,
                        color: accent,
                        size: 22,
                      ),
                      const SizedBox(width: 10),
                      const Expanded(
                        child: Text(
                          'اتصال به دستگاه دیگر',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                Divider(height: 1, color: border),
                Expanded(child: buildRightPane(context)),
              ],
            ),
          );

          final header = Container(
            padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 18),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: dark
                    ? const [Color(0xFF481124), Color(0xFFAB390F)]
                    : const [Color(0xFF781934), Color(0xFFAB390F)],
              ),
              borderRadius: BorderRadius.circular(22),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x28AB390F),
                  blurRadius: 28,
                  offset: Offset(0, 10),
                ),
              ],
            ),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(.12),
                    borderRadius: BorderRadius.circular(15),
                    border: Border.all(color: Colors.white.withOpacity(.16)),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(5),
                    child: Image.asset('assets/icon.png'),
                  ),
                ),
                const SizedBox(width: 14),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'فانوس دسک',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 22,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      SizedBox(height: 3),
                      Text(
                        'FANOOS DESK  •  دسترسی امن از راه دور',
                        style: TextStyle(
                          color: Color(0xFFFFE2A0),
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
                if (!bind.isDisableSettings())
                  Tooltip(
                    message: translate('Settings'),
                    child: IconButton(
                      onPressed: DesktopTabPage.onAddSetting,
                      icon: const Icon(
                        Icons.settings_rounded,
                        color: Colors.white,
                      ),
                    ),
                  ),
              ],
            ),
          );

          Widget content;
          if (isIncomingOnly) {
            content = localPanel;
          } else if (constraints.maxWidth < 860) {
            content = Column(
              children: [
                SizedBox(height: 360, child: localPanel),
                const SizedBox(height: 14),
                Expanded(child: remotePanel),
              ],
            );
          } else {
            content = Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SizedBox(width: 340, child: localPanel),
                const SizedBox(width: 14),
                Expanded(child: remotePanel),
              ],
            );
          }

          return ColoredBox(
            color: canvas,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  header,
                  const SizedBox(height: 14),
                  Expanded(child: content),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
'''
s = s[:build_start] + new_build + s[build_end:]
write(home_path, s)


# Keep the Fanoos accent consistent with upstream translucent highlights.
common_path = "flutter/lib/common.dart"
s = read(common_path)
s = s.replace("0x770071FF", "0x77AB390F").replace(
    "0xAA0071FF", "0xAAAB390F"
)
write(common_path, s)

print(
    "Applied Fanoos Persian-first locale/RTL, responsive dashboard, "
    "and visible server configuration"
)

for launcher in ("res/rustdesk.desktop", "res/rustdesk-link.desktop"):
    write(launcher, replace_once(read(launcher), "Name=RustDesk\n",
                                 "Name=Fanoos Desk\nName[fa]=فانوس دسک\n",
                                 launcher))
