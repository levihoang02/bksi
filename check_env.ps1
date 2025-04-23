Get-ChildItem -Path . -Recurse -Filter "*.env" | ForEach-Object {
    $file = $_.FullName
    Write-Host "`nChecking: $file" -ForegroundColor Cyan
    Select-String -Path $file -Pattern '^\s*[^#]+(\s+=|=\s+)' | ForEach-Object {
        "$($_.LineNumber): $($_.Line)"
    }
}
