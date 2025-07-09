; Inno Setup Script for CSVLotte
; This script creates a Windows installer for the CSVLotte application

[Setup]
AppName=CSVLotte
AppVersion=1.0.2-beta.9
AppPublisher=Lukas Waschul
AppPublisherURL=https://github.com/your-username/csvlotte
AppSupportURL=https://github.com/your-username/csvlotte/issues
AppUpdatesURL=https://github.com/your-username/csvlotte/releases
DefaultDirName={autopf}\CSVLotte
DefaultGroupName=CSVLotte
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=dist
OutputBaseFilename=CSVLotte-Setup-{#SetupSetting("AppVersion")}
SetupIconFile=src\csvlotte\assets\logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\CSVLotte.exe
UninstallDisplayName=CSVLotte
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "dist\CSVLotte.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\CSVLotte"; Filename: "{app}\CSVLotte.exe"
Name: "{group}\{cm:UninstallProgram,CSVLotte}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\CSVLotte"; Filename: "{app}\CSVLotte.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\CSVLotte"; Filename: "{app}\CSVLotte.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\CSVLotte.exe"; Description: "{cm:LaunchProgram,CSVLotte}"; Flags: nowait postinstall skipifsilent
