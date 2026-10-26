# TODO

- [ ] There's an issue with checking on the date...

A privacy.com transaction and the matching YNAB transaction can carry different dates.

If I give the privacy window room, the code as of (72e1ba9e4) will work, but it gets a lot more messy because it's very plausible that there's a same amount spent on transactions on different days. Ultimately though, since YNAB has the 'made aware' date, not the date of transaction, that might not matter. It just gets really sloppy.

- [ ] Update YNAB Category for known merchants
- [ ] Add tests
