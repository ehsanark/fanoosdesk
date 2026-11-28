Unicode true
!include "MUI2.nsh"
!include "LogicLib.nsh"
!define PACKAGE_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\FanoosDesk"
AllowSkipFiles off
Name "Fanoos Desk"
!define MUI_ICON "fanoos.ico"
!define MUI_UNICON "fanoos.ico"
OutFile "FanoosDesk-Setup-x64.exe"
InstallDir "$PROGRAMFILES64\FanoosDesk"
RequestExecutionLevel admin
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_TITLE "فانوس دسک آماده است"
!define MUI_FINISHPAGE_TEXT "نصب فانوس دسک روی این رایانه پایان یافت."
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "اجرای فانوس دسک"
!define MUI_FINISHPAGE_RUN_FUNCTION LaunchFanoos
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Farsi"
Function LaunchFanoos
  ExecShell "open" "$WINDIR\explorer.exe" '"$SMPROGRAMS\FanoosDesk\FanoosDesk.lnk"'
FunctionEnd

Section "Fanoos Desk"
  SetRegView 64
  SetShellVarContext all
  IfFileExists "$INSTDIR\fanoosdesk.exe" 0 first_install
  ExecWait '"$INSTDIR\fanoosdesk.exe" --uninstall-service' $0
  first_install:
  SetOutPath "$INSTDIR"
  File /r "windows-bundle\*.*"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FanoosDesk" "InstallLocation" "$INSTDIR"
  CopyFiles /SILENT "$SYSDIR\RuntimeBroker.exe" "$INSTDIR\RuntimeBroker_fanoosdesk.exe"
  WriteRegStr HKLM "${PACKAGE_KEY}" "BuildDate" "${BUILD_DATE}"
  WriteRegStr HKLM "${PACKAGE_KEY}" "DisplayVersion" "${ENGINE_VERSION} (Fanoos Build ${FANOOS_BUILD})"
  System::Call 'kernel32::SetEnvironmentVariableW(w "FANOOS_NSIS_INSTALL", w "1") i.r0'
  ClearErrors
  ExecWait '"$INSTDIR\fanoosdesk.exe" --install-service' $0
  ${If} ${Errors}
  ${OrIf} $0 != 0
    SetErrorLevel 1
    Abort "اجرای سرویس فانوس دسک ناموفق بود."
  ${EndIf}
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  CreateDirectory "$SMPROGRAMS\FanoosDesk"
  CreateShortcut "$SMPROGRAMS\FanoosDesk\FanoosDesk.lnk" "$INSTDIR\fanoosdesk.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FanoosDesk" "DisplayName" "Fanoos Desk"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FanoosDesk" "UninstallString" '"$INSTDIR\Uninstall.exe"'
SectionEnd
Section "Uninstall"
  SetRegView 64
  SetShellVarContext all
  ExecWait '"$INSTDIR\fanoosdesk.exe" --uninstall-service' $0
  Delete "$SMPROGRAMS\FanoosDesk\FanoosDesk.lnk"
  RMDir "$SMPROGRAMS\FanoosDesk"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FanoosDesk"
SectionEnd
