param(
    [int]$Width = 1280,
    [int]$Height = 720,
    [int]$X = 100,
    [int]$Y = 100,
    [int]$DurationSeconds = 0
)

# Simple file logger for diagnostics (appends to scripts\SetKodiWindow.log)
$logPath = Join-Path $PSScriptRoot "SetKodiWindow.log"
function Log($msg) {
    # Disabled logging
}
Log "--- Start SetKodiWindow: target client ${Width}x${Height} at ${X},${Y} ---"

Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

    [StructLayout(LayoutKind.Sequential)]
    public struct POINT { public int x; public int y; }
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int left; public int top; public int right; public int bottom; }

    [Serializable, StructLayout(LayoutKind.Sequential)]
    public struct WINDOWPLACEMENT {
        public int length;
        public int flags;
        public int showCmd;
        public POINT ptMinPosition;
        public POINT ptMaxPosition;
        public RECT rcNormalPosition;
    }

    [DllImport("user32.dll")] public static extern bool GetWindowPlacement(IntPtr hWnd, ref WINDOWPLACEMENT lpwndpl);
    [DllImport("user32.dll")] public static extern bool SetWindowPlacement(IntPtr hWnd, [In] ref WINDOWPLACEMENT lpwndpl);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, ref RECT lpRect);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr hwnd, int dwAttribute, out RECT pvAttribute, int cbAttribute);
    [DllImport("user32.dll", EntryPoint = "GetWindowLongPtr", SetLastError = true)]
    private static extern IntPtr _GetWindowLongPtr(IntPtr hWnd, int nIndex);
    [DllImport("user32.dll", EntryPoint = "GetWindowLong", SetLastError = true)]
    private static extern IntPtr _GetWindowLong(IntPtr hWnd, int nIndex);
    public static IntPtr GetWindowLongPtr(IntPtr hWnd, int nIndex) {
        if (IntPtr.Size == 8) return _GetWindowLongPtr(hWnd, nIndex);
        return _GetWindowLong(hWnd, nIndex);
    }
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool AdjustWindowRectEx(ref RECT lpRect, uint dwStyle, bool bMenu, uint dwExStyle);

    public const int SW_SHOWNORMAL = 1;
    public const int SW_RESTORE = 9;
    public const int GWL_STYLE = -16;
    public const int GWL_EXSTYLE = -20;
    public const uint SWP_NOZORDER = 0x0004;
    public const uint SWP_FRAMECHANGED = 0x0020;
    public const uint SWP_SHOWWINDOW = 0x0040;
    public const int DWMWA_EXTENDED_FRAME_BOUNDS = 9;
}
"@

# Try to find kodi process by name (case-insensitive)
$proc = Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match "(?i)^kodi$" }
$p = $proc | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
$hwnd = $null
if ($p) { $hwnd = $p.MainWindowHandle }

# Fallback: search processes whose MainWindowTitle contains "Kodi"
if (-not $hwnd -or $hwnd -eq 0) {
    $w = Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -and $_.MainWindowTitle -like "*Kodi*" } | Select-Object -First 1
    if ($w) { $hwnd = $w.MainWindowHandle }
}

if (-not $hwnd -or $hwnd -eq 0) {
    Write-Host "Kodi window handle not found."  
    exit 1
}

# First: update the stored WINDOWPLACEMENT so Windows "remembers" the new normal rect
$placement = New-Object Win32+WINDOWPLACEMENT
$placement.length = [Runtime.InteropServices.Marshal]::SizeOf($placement)
if ([Win32]::GetWindowPlacement($hwnd, [ref]$placement)) {
    # Check if window is maximized or fullscreen; if so, force restore to windowed mode
    if ($placement.showCmd -eq 3) {  # SW_MAXIMIZE
        $placement.showCmd = [Win32]::SW_SHOWNORMAL
        [Win32]::SetWindowPlacement($hwnd, [ref]$placement) | Out-Null
        Start-Sleep -Milliseconds 200
        # Re-get placement after restore
        [Win32]::GetWindowPlacement($hwnd, [ref]$placement) | Out-Null
    }
    # Use current position to keep on same monitor
    $currentX = $placement.rcNormalPosition.left
    $currentY = $placement.rcNormalPosition.top
    Write-Host "Using current position: ${currentX},${currentY}"
    Log "Using current position: ${currentX},${currentY}"
    # Use fixed frame-delta for Windows (approximate: 16 width, 39 height)
    $deltaW = 16
    $deltaH = 39
    $outerW = $Width + $deltaW
    $outerH = $Height + $deltaH
    Write-Host "Using fixed frame-delta: delta=${deltaW}x${deltaH}, outer=${outerW}x${outerH}"
    Log "Using fixed frame-delta: delta=${deltaW}x${deltaH}, outer=${outerW}x${outerH}"

    $placement.rcNormalPosition.left = $currentX
    $placement.rcNormalPosition.top = $currentY
    $placement.rcNormalPosition.right = $X + $outerW
    $placement.rcNormalPosition.bottom = $Y + $outerH
    # Use SHOWNORMAL for the stored placement but call Restore afterwards to ensure the window uses the new rect
    $placement.showCmd = [Win32]::SW_SHOWNORMAL
    [Win32]::SetWindowPlacement($hwnd, [ref]$placement) | Out-Null
}

# Then set current window position/size immediately (preserve z-order) and force a restore so Windows applies the stored normal rect
# Correct SWP constants: SWP_NOZORDER=0x0004, SWP_SHOWWINDOW=0x0040
$SWP_NOZORDER = 0x0004
## Quick initial attempts: some apps respond faster if we hammer the call a few times quickly
$quickAttempts = 3
for ($i=0; $i -lt $quickAttempts; $i++) {
    if ($hwnd -and $hwnd -ne 0) {
        [Win32]::SetWindowPlacement($hwnd, [ref]$placement) | Out-Null
        [Win32]::SetWindowPos($hwnd, [IntPtr]::Zero, $currentX, $currentY, $outerW, $outerH, [Win32]::SWP_NOZORDER) | Out-Null
        [Win32]::ShowWindow($hwnd, [Win32]::SW_RESTORE) | Out-Null
    }
    Start-Sleep -Milliseconds 100
}

# If requested, continuously reapply for DurationSeconds to outlast app resets (200ms interval)
if ($DurationSeconds -gt 0) {
    Log "Continuous reapply mode: duration ${DurationSeconds}s"
    $endTime = (Get-Date).AddSeconds($DurationSeconds)
    $contAttempt = 0
    $matched = $false
    while ((Get-Date) -lt $endTime) {
        if ($hwnd -and $hwnd -ne 0) {
            # Recalculate frame-delta each time for accuracy
            $sampleRect = New-Object Win32+RECT
            $sampleClient = New-Object Win32+RECT
            $dwmRect = New-Object Win32+RECT
            $haveOuter = $false
            $dwmRes = [Win32]::DwmGetWindowAttribute($hwnd, [Win32]::DWMWA_EXTENDED_FRAME_BOUNDS, [ref]$dwmRect, [Runtime.InteropServices.Marshal]::SizeOf($dwmRect))
            if ($dwmRes -eq 0) {
                $currentOuterW = $dwmRect.right - $dwmRect.left
                $currentOuterH = $dwmRect.bottom - $dwmRect.top
                $haveOuter = $true
            }
            if (-not $haveOuter -and [Win32]::GetWindowRect($hwnd, [ref]$sampleRect)) {
                $currentOuterW = $sampleRect.right - $sampleRect.left
                $currentOuterH = $sampleRect.bottom - $sampleRect.top
                $haveOuter = $true
            }
            # Use fixed frame-delta
            $deltaW = 16
            $deltaH = 39
            $adjustedOuterW = $Width + $deltaW
            $adjustedOuterH = $Height + $deltaH

            [Win32]::SetWindowPlacement($hwnd, [ref]$placement) | Out-Null
            [Win32]::SetWindowPos($hwnd, [IntPtr]::Zero, $currentX, $currentY, $adjustedOuterW, $adjustedOuterH, [Win32]::SWP_NOZORDER) | Out-Null
            [Win32]::ShowWindow($hwnd, [Win32]::SW_RESTORE) | Out-Null
            [Win32]::SetForegroundWindow($hwnd) | Out-Null
            Start-Sleep -Milliseconds 150
            $r = New-Object Win32+RECT
            if ([Win32]::GetWindowRect($hwnd, [ref]$r)) {
                $cw = $r.right - $r.left
                $ch = $r.bottom - $r.top
                $contAttempt++
                $line = "ContinuousAttempt " + $contAttempt + ": outer " + $cw + " x " + $ch + ", target outer " + $adjustedOuterW + " x " + $adjustedOuterH
                Write-Host $line
                Log $line
                if ([math]::Abs($cw - $adjustedOuterW) -le 2 -and [math]::Abs($ch - $adjustedOuterH) -le 2) { $matched = $true; break }
            }
        }
        Start-Sleep -Milliseconds 200
    }
    if ($matched) { Write-Host "Continuous mode: achieved target early"; Log "Continuous mode: achieved target early" }
    else { Write-Host "Continuous mode: finished without exact match"; Log "Continuous mode: finished without exact match" }
    Log "--- End SetKodiWindow (continuous mode) ---"
    exit 0
}
## Try multiple times: some applications (Kodi) may recreate the window after a resize,
## so we re-find and reapply placement until the visible size matches requested values.
$maxAttempts = 8
$attempt = 0
$ok = $false
while ($attempt -lt $maxAttempts) {
    # re-find handle if missing
    if (-not $hwnd -or $hwnd -eq 0) {
        $proc = Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match "(?i)^kodi$" -and $_.MainWindowHandle -ne 0 } | Select-Object -First 1
        if ($proc) { $hwnd = $proc.MainWindowHandle }
        else {
            $w = Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -and $_.MainWindowTitle -like "*Kodi*" } | Select-Object -First 1
            if ($w) { $hwnd = $w.MainWindowHandle }
        }
    }

    if ($hwnd -and $hwnd -ne 0) {
    # reapply stored placement and live size (use outer window size computed earlier)
    $applyMsg = "Applying: style=0x$([Convert]::ToString($style,16)), exstyle=0x$([Convert]::ToString($exstyle,16)), outer=${outerW}x${outerH}, client=${Width}x${Height}"
    Write-Host $applyMsg
    Log $applyMsg
        [Win32]::SetWindowPlacement($hwnd, [ref]$placement) | Out-Null
        $flags = [Win32]::SWP_NOZORDER -bor [Win32]::SWP_FRAMECHANGED -bor [Win32]::SWP_SHOWWINDOW
        [Win32]::SetWindowPos($hwnd, [IntPtr]::Zero, $currentX, $currentY, $outerW, $outerH, $flags) | Out-Null
        [Win32]::ShowWindow($hwnd, [Win32]::SW_RESTORE) | Out-Null
        [Win32]::SetForegroundWindow($hwnd) | Out-Null

        Start-Sleep -Milliseconds 500

        $rect = New-Object Win32+RECT
        if ([Win32]::GetWindowRect($hwnd, [ref]$rect)) {
            $currentW = $rect.right - $rect.left
            $currentH = $rect.bottom - $rect.top
            # also get client rect for diagnostics
            $clientRect = New-Object Win32+RECT
            if ([Win32]::GetClientRect($hwnd, [ref]$clientRect)) {
                $clientW = $clientRect.right - $clientRect.left
                $clientH = $clientRect.bottom - $clientRect.top
            } else { $clientW = -1; $clientH = -1 }

            $attemptMsg = "Attempt $($attempt+1): outer ${currentW}x${currentH}, client ${clientW}x${clientH}, target outer ${outerW}x${outerH}, target client ${Width}x${Height}"
            Write-Host $attemptMsg
            Log $attemptMsg
            $tol = 2
            if (([math]::Abs($currentW - $outerW) -le $tol) -and ([math]::Abs($currentH - $outerH) -le $tol) -and ([math]::Abs($clientW - $Width) -le $tol) -and ([math]::Abs($clientH - $Height) -le $tol)) {
                $ok = $true
                break
            }
        } else {
            Write-Host "Attempt $($attempt+1): GetWindowRect failed for hwnd $hwnd"
            Log "Attempt $($attempt+1): GetWindowRect failed for hwnd $hwnd"
        }
    } else {
    Write-Host "Attempt $($attempt+1): Kodi window not found, retrying..."
    Log "Attempt $($attempt+1): Kodi window not found, retrying..."
    }

    Start-Sleep -Milliseconds 300
    $attempt++
}

# If we didn't reach it, try one final recalculation using a measured frame-delta and reapply
if (-not $ok) {
    $sampleRect = New-Object Win32+RECT
    $sampleClient = New-Object Win32+RECT
    if ([Win32]::GetWindowRect($hwnd, [ref]$sampleRect) -and [Win32]::GetClientRect($hwnd, [ref]$sampleClient)) {
        $deltaW = ($sampleRect.right - $sampleRect.left) - ($sampleClient.right - $sampleClient.left)
        $deltaH = ($sampleRect.bottom - $sampleRect.top) - ($sampleClient.bottom - $sampleClient.top)
        if ($deltaW -ge 0 -and $deltaH -ge 0) {
            $outerW = $Width + $deltaW
            $outerH = $Height + $deltaH
            $finalMsg = "Final fallback: applying outer ${outerW}x${outerH} (delta ${deltaW}x${deltaH})"
            Write-Host $finalMsg
            Log $finalMsg
            [Win32]::SetWindowPos($hwnd, [IntPtr]::Zero, $currentX, $currentY, $outerW, $outerH, [Win32]::SWP_NOZORDER) | Out-Null
            Start-Sleep -Milliseconds 400
        }
    }
}

if ($ok) {
    $s = "Set window: $hwnd -> $X,$Y ${Width}x${Height} (placement applied)"
    Write-Host $s
    Log $s
} else {
    $f = "Failed to reach target size after $maxAttempts attempts. Last known hwnd: $hwnd"
    Write-Host $f
    Log $f
}

Log "--- End SetKodiWindow ---"
