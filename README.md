STARTUP:
  This program is meant to be run on a single linux machine. To start up the
  metadata server, open a terminal that points to the proper directory, then
  use the command 'python3 server.py'

  SERVER EXPLANATION:
    this is rather a simple file. it consits of a main method that listens for
    incoming client connections, and once one is received, spawns a new thread
    to supply the connection with the necessary information, then closes that
    connection once all needed info has been sent and continues listening.

  Once the metadata server is running, clients can be run in new terminal windows
  from the same directory by using 'python3 client.py'

    CLIENT EXPLANATION:
      the client process is where the majority of the work for this project was
      focused. It starts by connection to M to gain info for how to join the P2P
      network. once it has this info, it attempts connection, and traverses
      connections until it finds an open connection. Once connected, it listens
      for new connections and either accepts or forwards these connections,
      depending on its current state. Once a client is done accepting connections,
      it is ready to allow for file downloads, or download files of its own.

P2P NETWORK:
  TOPO will print out once you have stopped waiting for servers to
  connect to the P2P network, for that particular server.
  It only displays connections held by the server socket, as connections held by
  the client socket will be displayed in that peers TOPO information upon exit.

  To help with flow of the project, accept calls on server sockets are set to
  error check for timeouts, the default timeout value is 30 seconds, if you feel
  that this needs to be tweaked to be shorter/longer, it is the first global variable
  in the client.py file and can be edited.

  Along with these timeout calls comes anther important facet of my project. To
  ensure proper behavior, all servers in the P2P network must be currently displaying
  either ***Waiting to Fill Connections*** or ***Waiting to Forward Connections***,
  if any servers are waiting for a prompt of any kind, such as a confirmation of
  continue waiting, the connection process WILL NOT work correctly.

DOWNLOADING FILES:
  If you wish to download a file, either one that is a member of the P2P network
  or that is not part of the P2P network, all servers that you wish to connect
  to the P2P group MUST be connected before doing any file downloads.
  This is due to port assignment from M. If a process attempts to download a file
  before all P2P members are connected.

  If you wish to download a file without becoming a member of the P2P network,
  you will be prompted similarly to how you would for joining the P2P network.
  this is so M can properly assign port numbers to the sockets. The flag to access
  is still P2P, this was to maximize code re-usage.

  To download a file from a process that joined the P2P group, the process first
  needs to:
  -Stop accepting new connections(this will pop up as a prompt (discussed above))
  -Choose Download File (2) when prompted

  To ensure all P2P Members are ready to provide file downloads:
  -Stop accepting new connections(this will pop up as a prompt (discussed above))
  -Choose Stay on P2P (1) when prompted
      this ensures that the process is listening to file download requests

  'Downloading' a file for my project is handled by the member opening said file,
  reading its contents, and sending the contents as a message to the requesting
  member. I chose this implementation because the entire project is run locally,
  with all servers looking in the same location for files, so downloading copies
  of these files every time would be redundant.

  Because all processes run on one machine, splitting up which P2P members grant
  access to which files is done by server number. For example, if you wanted to
  download a file with the number '1' in the name, this would be allowed by the
  first server in the P2P network.

  If a process attempts to download a file that it would theoretically already have,
  based on my implementation scheme, it is simply prompted that the file is
  'already downloaded' and looped back to asking for a new file name.
    -i.e. if peer 3 requested ssn3

  This selection process mentioned in the above paragraph is handled by selecting
  port numbers based on file name. This circumvents the traversal of actual
  connections from peer to peer, and instead directly hops to the server it will
  attempt to access the file from. This is able to be done because we know what
  the port number for each of these members is going to be.
