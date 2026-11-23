Unicode true
!include "MUI2.nsh"
Name "Fanoos Desk"
!define MUI_ICON "fanoos.ico"
!define MUI_UNICON "fanoos.ico"
OutFile "FanoosDesk-Setup-x64.exe"
InstallDir "$PROGRAMFILES64\FanoosDesk"
RequestExecutionLevel admin
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Farsi"
Section "Fanoos Desk"
  SetRegView 64
  SetShellVarContext all
  SetOutPath "$INSTDIR"
  File /r "windows-bundle\*.*"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FanoosDesk" "InstallLocation" "$INSTDIR"
  CopyFiles /SILENT "$SYSDIR\RuntimeBroker.exe" "$INSTDIR\RuntimeBroker_fanoosdesk.exe"
  ExecWait '"$INSTDIR\fanoosdesk.exe" --install-service' $0
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
