# Amostra a taxa de descarga da bateria a 1 Hz no Windows e grava CSV carimbado.
# Uso:  powershell -ExecutionPolicy Bypass -File src\medir_windows.ps1 -Nome antigo_R1 -Palavra PALAVRA
param(
  [Parameter(Mandatory=$true)][string]$Nome,
  [Parameter(Mandatory=$true)][string]$Palavra,
  [int]$Duracao = 600
)
$saida = Join-Path $PSScriptRoot "..\dados\logs\$Nome.csv"
$cs = Get-CimInstance Win32_ComputerSystem
"# maquina=$env:COMPUTERNAME;fabricante=$($cs.Manufacturer);modelo=$($cs.Model);palavra=$Palavra;inicio=$(Get-Date -Format o)" | Out-File $saida -Encoding utf8
"timestamp,epoch,potencia_w,energia_wh,bateria_pct,status" | Out-File $saida -Append -Encoding utf8
Write-Host "Maquina: $env:COMPUTERNAME | $($cs.Model) | palavra-chave: $Palavra"
for ($k = 0; $k -lt $Duracao; $k++) {
  $b = Get-CimInstance -Namespace root\wmi -ClassName BatteryStatus | Select-Object -First 1
  $agora = Get-Date
  $p = $b.DischargeRate / 1000.0
  $e = $b.RemainingCapacity / 1000.0
  $pct = (Get-CimInstance Win32_Battery | Select-Object -First 1).EstimatedChargeRemaining
  $epoch = [DateTimeOffset]::new($agora).ToUnixTimeMilliseconds() / 1000.0
  "$($agora.ToString('s')),$epoch,$p,$e,$pct,Discharging" | Out-File $saida -Append -Encoding utf8
  if ($k % 30 -eq 0) { Write-Host "$($agora.ToString('HH:mm:ss'))  $p W  $pct%  [$Palavra]" }
  Start-Sleep -Milliseconds (1000 - ((Get-Date) - $agora).TotalMilliseconds)
}
Write-Host "Fim. $saida"
