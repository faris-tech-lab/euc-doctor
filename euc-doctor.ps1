param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

py -m euc_doctor @Args
