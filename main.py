from bot import Bot

def main():

    regis = Bot()
    regis.login()
    regis.say("Regis Philbot!")
    regis.logout()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit(1)
