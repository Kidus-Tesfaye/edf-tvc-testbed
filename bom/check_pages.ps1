param([string]$path)
$w = New-Object -ComObject Word.Application
$w.Visible = $false
try {
  $doc = $w.Documents.Open($path, $false, $true)
  $pages = $doc.ComputeStatistics(2)          # wdStatisticPages
  $t = $doc.Tables.Item(1)
  $startPage = $t.Range.Information(1)        # wdActiveEndPageNumber of the (collapsed-start) range
  $r = $t.Cell($t.Rows.Count, 1).Range
  $r.Collapse(0)                              # wdCollapseEnd
  $endPage = $r.Information(3)                # wdActiveEndAdjustedPageNumber
  $rs = $t.Range
  $rs.Collapse(1)                             # wdCollapseStart
  $startPage = $rs.Information(3)
  Write-Output ("pages=$pages tables=" + $doc.Tables.Count + " tableStartPage=$startPage tableEndPage=$endPage hyperlinks=" + $doc.Hyperlinks.Count + " rows=" + $t.Rows.Count)
  $pdf = [System.IO.Path]::ChangeExtension($path, '.pdf')
  $doc.ExportAsFixedFormat($pdf, 17)          # wdExportFormatPDF
  $doc.Close($false)
} finally { $w.Quit() }
