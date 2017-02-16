/* A simple user client in C.
   Contains a TCP client and an 'AI'.
   The AI moves in a straight line and fires missiles
   whenever it can see something.
 */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 

#define BUFSIZE 4096

// The possible moves for the robot
#define MOVE_RESIGN -1
#define MOVE_NONE 0
#define MOVE_SPEED_UP 1
#define MOVE_SLOW_DOWN 2
#define MOVE_TURN_RIGHT 3
#define MOVE_TURN_LEFT 4
#define MOVE_FIRE_MISSILE 5
#define MOVE_FIRE_LASER 6

int sockfd;

void error(char *msg)
{
    perror(msg);
    exit(0);
}
void tcp_send(char *buf)
{
  int n = write(sockfd, buf, strlen(buf));
  if (n < 0) 
    error("ERROR writing to socket");
}
void resign(int sig)
{
    printf("Resigning.\n");
    // Send MOVE_RESIGN
    tcp_send("-1");
    exit(0);
}

int main(int argc, char **argv)
{
    int portno, n;
    struct sockaddr_in serveraddr;
    struct hostent *server;
    char *hostname;
    char buf[BUFSIZE];
    int team_colour = 0;

    // Catch SIGINT so that we can send a resignation to the server.
    (void) signal(SIGINT, resign);

    /* check command line arguments */
    if (argc != 4) {
       fprintf(stderr,"usage: %s <hostname> <port> <team colour>\n", argv[0]);
       exit(0);
    }
    hostname = argv[1];
    portno = atoi(argv[2]);
    team_colour = atoi(argv[3]);

    /* socket: create the socket */
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) 
        error("ERROR opening socket");

    /* gethostbyname: get the server's DNS entry */
    server = gethostbyname(hostname);
    if (server == NULL) {
        fprintf(stderr,"ERROR, no such host as %s\n", hostname);
        exit(0);
    }

    /* build the server's Internet address */
    bzero((char *) &serveraddr, sizeof(serveraddr));
    serveraddr.sin_family = AF_INET;
    bcopy((char *)server->h_addr, 
	  (char *)&serveraddr.sin_addr.s_addr, server->h_length);
    serveraddr.sin_port = htons(portno);

    /* connect: create a connection with the server */
    if (connect(sockfd, (const struct sockaddr *)&serveraddr, sizeof(serveraddr)) < 0) 
      error("ERROR connecting");

    // First of all send team colour
    snprintf(buf, BUFSIZE, "%d", team_colour);
    tcp_send(buf);

    while(1)
    {
      /* Get robot/world state from server */
      bzero(buf, BUFSIZE);
      n = read(sockfd, buf, BUFSIZE);
      if (n < 0) 
        error("ERROR reading from socket");

      //printf("Got robot/world state from server:\n%s\n", buf);

      // First check if the server is telling us to die.
      if(strcmp(buf, "die")==0)
      {
        printf("Kicked by server.\n");
        return 0;
      }

      // Check if the objectsInView list is empty.
      // This would look like:
      // {"objectsInView": []}
      char *cp = strstr(buf, "objectsInView\": [");
      if(cp==NULL)
        error("ERROR: didn't get worldstate from server.\n");
      // Pointer is at the 'o' of objects.
      cp += 17;
      // Now if c is ']', it means the list is empty.
      int listIsEmpty = ( *cp==']' );
      int move = MOVE_SPEED_UP;
      if(!listIsEmpty)
      {
        move = MOVE_FIRE_MISSILE;
      }
      // Write move to buffer
      snprintf(buf, BUFSIZE, "%d", move);

      /* Get move from the user */
      /*
      printf("Please enter move: ");
      printf(">>");
      bzero(buf, BUFSIZE);
      fgets(buf, BUFSIZE, stdin);
       */

      /* Send the buffer to the server */
      tcp_send(buf);
    }

    close(sockfd);
    return 0;
}
