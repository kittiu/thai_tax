import click


def after_install():
	try:
		print("Setting up Thai Tax...")

		click.secho("Thank you for installing Thai Tax!", fg="green")

	except Exception as e:
		BUG_REPORT_URL = "https://github.com/kittiu/thai_tax/issues/new"
		click.secho(
			"Installation for Thai Tax app failed due to an error."
			" Please try re-installing the app or"
			f" report the issue on {BUG_REPORT_URL} if not resolved.",
			fg="bright_red",
		)
		raise e
