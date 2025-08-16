# Frontend Module Specifications

> **Comprehensive frontend architecture for Agentic AI Acceleration with A2A Protocol visualization and MCP integration**

## 1. Technology Stack & Architecture

### 1.1 Core Framework Matrix

| Technology | Version | Purpose | Status | Health Check URL |
|------------|---------|---------|--------|------------------|
| Next.js | ^15.4.0 | React framework with App Router | ✅ Active | `http://localhost:3000/api/health` |
| React | ^19.1.0 | UI library with concurrent features | ✅ Active | Built into Next.js |
| TypeScript | ^5.4.0 | Type safety and developer experience | ✅ Active | Compile-time |
| Tailwind CSS | ^3.4.0 | Utility-first CSS framework | ✅ Active | Build-time |

### 1.2 Enhanced Dependencies with A2A & MCP Support

```json
{
  "dependencies": {
    "next": "^15.4.0",
    "react": "^19.1.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.4.0",
    
    // A2A Protocol & Real-time Communication
    "socket.io-client": "^4.7.0",
    "@socket.io/component-emitter": "^3.1.0",
    "ws": "^8.16.0",
    "reconnecting-websocket": "^4.4.0",
    
    // MCP Integration
    "mcp-client": "^0.1.0",
    "jsonrpc-websocket": "^3.1.5",
    "mcp-discovery": "^0.1.0",
    
    // UI Components & Styling
    "tailwindcss": "^3.4.0",
    "@tailwindcss/forms": "^0.5.7",
    "@tailwindcss/typography": "^0.5.10",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "lucide-react": "^0.363.0",
    "@heroicons/react": "^2.1.0",
    
    // Enhanced Radix UI Components
    "@radix-ui/react-accordion": "^1.1.2",
    "@radix-ui/react-alert-dialog": "^1.0.5",
    "@radix-ui/react-avatar": "^1.0.4",
    "@radix-ui/react-checkbox": "^1.0.4",
    "@radix-ui/react-collapsible": "^1.0.3",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-hover-card": "^1.0.7",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-menubar": "^1.0.4",
    "@radix-ui/react-navigation-menu": "^1.1.4",
    "@radix-ui/react-popover": "^1.0.7",
    "@radix-ui/react-progress": "^1.0.3",
    "@radix-ui/react-radio-group": "^1.1.3",
    "@radix-ui/react-scroll-area": "^1.0.5",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-separator": "^1.0.3",
    "@radix-ui/react-sheet": "^1.0.5",
    "@radix-ui/react-slider": "^1.1.2",
    "@radix-ui/react-switch": "^1.0.3",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "@radix-ui/react-toggle": "^1.0.3",
    "@radix-ui/react-toggle-group": "^1.0.4",
    "@radix-ui/react-tooltip": "^1.0.7"
  }
}
```

### 1.3 A2A Protocol & Visualization Stack
```json
{
  "a2a-visualization": {
    "reactflow": "^11.11.0",
    "@xyflow/react": "^12.0.0",
    "cytoscape": "^3.28.0",
    "cytoscape-react": "^2.0.0",
    "vis-network": "^9.1.0",
    "d3": "^7.9.0",
    "d3-hierarchy": "^3.1.0",
    "d3-force": "^3.0.0",
    "@types/d3": "^7.4.0",
    
    // Agent Communication Visualization
    "mermaid": "^10.9.0",
    "jointjs": "^3.7.0",
    "fabric": "^5.3.0"
  }
}
```

### 1.4 State Management & Data Fetching
```json
{
  "state-management": {
    "zustand": "^4.5.0",
    "immer": "^10.0.0",
    "jotai": "^2.6.0",
    
    // Enhanced React Query with Real-time
    "@tanstack/react-query": "^5.28.0",
    "@tanstack/react-query-devtools": "^5.28.0",
    "@tanstack/react-query-persist-client-core": "^5.28.0",
    
    // HTTP & WebSocket Clients
    "axios": "^1.6.0",
    "swr": "^2.2.0",
    "ky": "^1.2.0"
  }
}
```

## 2. Enhanced Frontend Architecture with A2A Protocol

### 2.1 A2A Protocol Frontend Integration

```typescript
// lib/a2a-protocol-client.ts
interface A2AProtocolClient {
  // Connection Management
  connect(agentId: string): Promise<void>;
  disconnect(): Promise<void>;
  isConnected(): boolean;
  
  // Message Handling with Type Safety
  sendMessage(message: A2AMessage): Promise<A2AMessageResult>;
  broadcastMessage(message: Omit<A2AMessage, 'to'>): Promise<A2ABroadcastResult>;
  subscribeToMessages(agentId: string, handler: A2AMessageHandler): void;
  
  // Real-time Coordination
  subscribeToCoordination(executionId: string, handler: CoordinationEventHandler): void;
  getCoordinationState(executionId: string): Promise<CoordinationContext>;
  
  // Protocol Events
  onAgentJoined(handler: (agentId: string) => void): void;
  onAgentLeft(handler: (agentId: string) => void): void;
  onConsensusUpdate(handler: (consensus: ConsensusState) => void): void;
}

// A2A Message Types for Frontend
interface A2AMessage {
  id: string;
  version: string;
  from: string;
  to: string | '*';
  type: 'request' | 'response' | 'broadcast' | 'negotiation' | 'coordination';
  intent: string;
  payload: {
    data: any;
    metadata: {
      priority: number;
      timeout: number;
      correlationId?: string;
      conversationId?: string;
    };
    context: {
      workflowId?: string;
      sessionId?: string;
      traceId: string;
    };
  };
  timestamp: string;
  uiMetadata?: {
    visualization?: {
      color: string;
      icon: string;
      animation: 'pulse' | 'flow' | 'bounce';
    };
    displayName?: string;
    description?: string;
  };
}
```

### 2.2 MCP Client Integration

```typescript
// lib/mcp-client.ts
interface MCPClientManager {
  // Server Discovery & Connection
  discoverServers(): Promise<MCPServer[]>;
  connectToServer(serverUrl: string, apiKey?: string): Promise<MCPConnection>;
  disconnectFromServer(serverId: string): Promise<void>;
  
  // Tool Discovery & Execution
  listTools(serverId: string): Promise<MCPTool[]>;
  executeTool(serverId: string, toolName: string, parameters: any): Promise<MCPToolResult>;
  
  // Real-time Updates
  subscribeToServerUpdates(serverId: string, handler: MCPUpdateHandler): void;
  subscribeToToolDiscovery(handler: ToolDiscoveryHandler): void;
  
  // Health Monitoring
  getServerHealth(serverId: string): Promise<MCPServerHealth>;
  subscribeToHealthUpdates(handler: HealthUpdateHandler): void;
}

interface MCPServer {
  id: string;
  name: string;
  url: string;
  status: 'connected' | 'disconnected' | 'error';
  capabilities: string[];
  toolCount: number;
  healthUrl: string;
  lastDiscovery: string;
  metadata: {
    version: string;
    description?: string;
    tags: string[];
  };
}

interface MCPTool {
  id: string;
  name: string;
  description: string;
  serverId: string;
  serverUrl: string;
  parameters: {
    [paramName: string]: {
      type: string;
      description: string;
      required: boolean;
      example: any;
    };
  };
  output: {
    type: string;
    description: string;
    example: any;
  };
  uiSchema?: {
    category: string;
    icon: string;
    color: string;
    inputComponent?: 'form' | 'code' | 'file' | 'json';
    outputComponent?: 'text' | 'json' | 'table' | 'chart';
  };
}
```

### 2.3 Real-time Dashboard Components

```typescript
// components/dashboard/a2a-coordination-monitor.tsx
interface A2ACoordinationMonitorProps {
  executionId: string;
  workflowId: string;
  onMessageClick?: (message: A2AMessage) => void;
}

export function A2ACoordinationMonitor({ 
  executionId, 
  workflowId, 
  onMessageClick 
}: A2ACoordinationMonitorProps) {
  const [coordinationState, setCoordinationState] = useState<CoordinationContext>();
  const [messages, setMessages] = useState<A2AMessage[]>([]);
  const [consensusLevel, setConsensusLevel] = useState(0);
  
  // Real-time coordination monitoring
  const { isConnected, sendMessage } = useA2AProtocol(executionId);
  
  // WebSocket subscription for live updates
  useEffect(() => {
    const unsubscribe = subscribeToCoordination(executionId, (event) => {
      switch (event.type) {
        case 'a2a_message_sent':
        case 'a2a_message_received':
          setMessages(prev => [...prev, event.data.a2aMessage]);
          break;
        case 'consensus_update':
          setConsensusLevel(event.data.coordination.consensus);
          break;
        case 'coordination_update':
          setCoordinationState(event.data.coordination);
          break;
      }
    });
    
    return unsubscribe;
  }, [executionId]);
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Real-time Message Flow */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            A2A Message Flow
            {isConnected && (
              <Badge variant="success">
                <Zap className="w-3 h-3 mr-1" />
                Live
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <A2AMessageFlow 
            messages={messages}
            onMessageClick={onMessageClick}
            coordinationState={coordinationState}
          />
        </CardContent>
      </Card>
      
      {/* Consensus Tracking */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Consensus Level
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ConsensusVisualization 
            level={consensusLevel}
            participants={coordinationState?.participants || []}
            threshold={coordinationState?.consensusThreshold || 0.7}
          />
        </CardContent>
      </Card>
      
      {/* Agent Collaboration Network */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="w-5 h-5" />
            Agent Collaboration Network
          </CardTitle>
        </CardHeader>
        <CardContent>
          <AgentNetworkVisualization 
            coordinationState={coordinationState}
            messages={messages}
            interactive={true}
          />
        </CardContent>
      </Card>
    </div>
  );
}
```

### 2.4 MCP Server Management Interface

```typescript
// components/tools/mcp-server-dashboard.tsx
export function MCPServerDashboard() {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [selectedServer, setSelectedServer] = useState<MCPServer | null>(null);
  const [discoveredTools, setDiscoveredTools] = useState<MCPTool[]>([]);
  
  const { 
    discoverServers, 
    connectToServer, 
    listTools, 
    getServerHealth 
  } = useMCPClient();
  
  // Auto-discovery of MCP servers
  useEffect(() => {
    const discoverAndConnect = async () => {
      const discovered = await discoverServers();
      setServers(discovered);
      
      // Auto-connect to healthy servers
      for (const server of discovered) {
        if (server.status === 'disconnected') {
          try {
            await connectToServer(server.url);
          } catch (error) {
            console.warn(`Failed to connect to MCP server ${server.name}:`, error);
          }
        }
      }
    };
    
    discoverAndConnect();
  }, []);
  
  // Real-time server health monitoring
  const { data: serverHealth } = useQuery({
    queryKey: ['mcp-server-health', selectedServer?.id],
    queryFn: () => selectedServer ? getServerHealth(selectedServer.id) : null,
    enabled: !!selectedServer,
    refetchInterval: 30000, // Check every 30 seconds
  });
  
  return (
    <div className="space-y-6">
      {/* Server Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {servers.map((server) => (
          <MCPServerCard
            key={server.id}
            server={server}
            onSelect={setSelectedServer}
            isSelected={selectedServer?.id === server.id}
          />
        ))}
      </div>
      
      {/* Server Details Panel */}
      {selectedServer && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>{selectedServer.name}</span>
              <MCPServerStatusBadge server={selectedServer} />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="tools">
              <TabsList>
                <TabsTrigger value="tools">Discovered Tools</TabsTrigger>
                <TabsTrigger value="health">Health Status</TabsTrigger>
                <TabsTrigger value="logs">Connection Logs</TabsTrigger>
              </TabsList>
              
              <TabsContent value="tools">
                <MCPToolGrid 
                  serverId={selectedServer.id}
                  tools={discoveredTools}
                />
              </TabsContent>
              
              <TabsContent value="health">
                <MCPServerHealthPanel 
                  server={selectedServer}
                  health={serverHealth}
                />
              </TabsContent>
              
              <TabsContent value="logs">
                <MCPConnectionLogs serverId={selectedServer.id} />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
```

## 3. Enhanced Component Architecture

### 3.1 Agent Registry with A2A Cards

```typescript
// components/agents/agent-registry-card.tsx
interface AgentRegistryCardProps {
  agent: Agent;
  a2aCapabilities?: A2ACapability[];
  onMessageAgent?: (agentId: string) => void;
  onViewA2ACard?: (agentId: string) => void;
}

export function AgentRegistryCard({ 
  agent, 
  a2aCapabilities, 
  onMessageAgent, 
  onViewA2ACard 
}: AgentRegistryCardProps) {
  const [isOnline, setIsOnline] = useState(false);
  const [lastSeen, setLastSeen] = useState<Date>();
  
  // Monitor agent availability
  const { data: agentStatus } = useQuery({
    queryKey: ['agent-status', agent.id],
    queryFn: () => getAgentStatus(agent.id),
    refetchInterval: 15000,
  });
  
  useEffect(() => {
    if (agentStatus) {
      setIsOnline(agentStatus.status === 'online');
      setLastSeen(new Date(agentStatus.lastSeen));
    }
  }, [agentStatus]);
  
  return (
    <Card className="relative group hover:shadow-lg transition-shadow">
      {/* Online Status Indicator */}
      <div className="absolute top-3 right-3 flex items-center gap-2">
        <div className={cn(
          "w-2 h-2 rounded-full",
          isOnline ? "bg-green-500" : "bg-gray-400"
        )} />
        <span className="text-xs text-muted-foreground">
          {isOnline ? 'Online' : lastSeen ? `Last seen ${formatDistanceToNow(lastSeen)} ago` : 'Offline'}
        </span>
      </div>
      
      <CardHeader>
        <div className="flex items-center gap-3">
          <Avatar className="w-10 h-10">
            <AvatarImage src={`/agents/${agent.framework}.png`} />
            <AvatarFallback>{agent.name.charAt(0)}</AvatarFallback>
          </Avatar>
          <div>
            <CardTitle className="text-lg">{agent.name}</CardTitle>
            <p className="text-sm text-muted-foreground">
              {agent.framework} • {agent.skills.length} skills
            </p>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <p className="text-sm mb-4">{agent.description}</p>
        
        {/* A2A Capabilities */}
        {a2aCapabilities && a2aCapabilities.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium mb-2">A2A Capabilities</h4>
            <div className="flex flex-wrap gap-1">
              {a2aCapabilities.map((capability) => (
                <Badge key={capability.name} variant="secondary" className="text-xs">
                  {capability.name}
                </Badge>
              ))}
            </div>
          </div>
        )}
        
        {/* Skills */}
        <div className="mb-4">
          <h4 className="text-sm font-medium mb-2">Skills</h4>
          <div className="flex flex-wrap gap-1">
            {agent.skills.slice(0, 3).map((skill) => (
              <Badge key={skill} variant="outline" className="text-xs">
                {skill}
              </Badge>
            ))}
            {agent.skills.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{agent.skills.length - 3} more
              </Badge>
            )}
          </div>
        </div>
        
        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="flex-1">
            <Play className="w-3 h-3 mr-1" />
            Execute
          </Button>
          {isOnline && onMessageAgent && (
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => onMessageAgent(agent.id)}
            >
              <MessageSquare className="w-3 h-3" />
            </Button>
          )}
          {onViewA2ACard && (
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => onViewA2ACard(agent.id)}
            >
              <ExternalLink className="w-3 h-3" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

### 3.2 Workflow Designer with A2A Coordination

```typescript
// components/workflows/enhanced-workflow-designer.tsx
export function EnhancedWorkflowDesigner() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [coordinationType, setCoordinationType] = useState<CoordinationType>('sequential');
  const [a2aEnabled, setA2AEnabled] = useState(false);
  
  // Enhanced node types with A2A support
  const nodeTypes = useMemo(() => ({
    agent: (props: NodeProps) => (
      <AgentNode 
        {...props} 
        a2aEnabled={a2aEnabled}
        coordinationType={coordinationType}
      />
    ),
    tool: ToolNode,
    condition: ConditionNode,
    parallel: ParallelNode,
    consensus: ConsensusNode, // New node type for consensus coordination
    a2aBroadcast: A2ABroadcastNode, // New node type for A2A broadcasting
  }), [a2aEnabled, coordinationType]);
  
  // A2A Message Flow Visualization
  const [a2aMessages, setA2AMessages] = useState<A2AMessage[]>([]);
  const [showA2AFlow, setShowA2AFlow] = useState(false);
  
  return (
    <div className="flex h-screen">
      {/* Enhanced Node Palette */}
      <div className="w-80 border-r bg-muted/50 flex flex-col">
        <div className="p-4 border-b">
          <h3 className="font-semibold mb-3">Workflow Designer</h3>
          
          {/* Coordination Settings */}
          <div className="space-y-3">
            <div>
              <Label htmlFor="coordination-type">Coordination Type</Label>
              <Select value={coordinationType} onValueChange={setCoordinationType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sequential">Sequential</SelectItem>
                  <SelectItem value="parallel">Parallel</SelectItem>
                  <SelectItem value="dynamic">Dynamic</SelectItem>
                  <SelectItem value="consensus">Consensus</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-center space-x-2">
              <Switch 
                id="a2a-enabled" 
                checked={a2aEnabled}
                onCheckedChange={setA2AEnabled}
              />
              <Label htmlFor="a2a-enabled">Enable A2A Protocol</Label>
            </div>
            
            {a2aEnabled && (
              <div className="flex items-center space-x-2">
                <Switch 
                  id="show-a2a-flow" 
                  checked={showA2AFlow}
                  onCheckedChange={setShowA2AFlow}
                />
                <Label htmlFor="show-a2a-flow">Show A2A Message Flow</Label>
              </div>
            )}
          </div>
        </div>
        
        <ScrollArea className="flex-1">
          <EnhancedNodePalette 
            coordinationType={coordinationType}
            a2aEnabled={a2aEnabled}
          />
        </ScrollArea>
      </div>
      
      {/* Flow Canvas */}
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <MiniMap />
          <Background variant="dots" gap={12} size={1} />
          
          {/* A2A Message Flow Overlay */}
          {showA2AFlow && a2aEnabled && (
            <A2AMessageFlowOverlay 
              messages={a2aMessages}
              nodes={nodes}
              edges={edges}
            />
          )}
        </ReactFlow>
        
        {/* Workflow Execution Panel */}
        <div className="absolute bottom-4 left-4 right-4">
          <WorkflowExecutionPanel
            workflow={{ nodes, edges }}
            coordinationType={coordinationType}
            a2aEnabled={a2aEnabled}
            onExecutionStart={(executionId) => {
              // Subscribe to A2A messages for this execution
              if (a2aEnabled) {
                subscribeToA2AMessages(executionId, setA2AMessages);
              }
            }}
          />
        </div>
      </div>
    </div>
  );
}
```

### 3.3 Real-time Chat with A2A Agent Communication

```typescript
// components/chat/enhanced-chat-interface.tsx
export function EnhancedChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [activeAgents, setActiveAgents] = useState<string[]>([]);
  const [a2aMessages, setA2AMessages] = useState<A2AMessage[]>([]);
  const [showA2APane, setShowA2APane] = useState(false);
  
  const { sendMessage, isConnected } = useChatWebSocket();
  const { subscribeToA2A } = useA2AProtocol();
  
  // Enhanced message handling with A2A awareness
  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;
    
    const chatMessage: ChatMessage = {
      id: nanoid(),
      role: 'user',
      content: currentMessage,
      type: 'text',
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, chatMessage]);
    setCurrentMessage('');
    
    // Send to chat service
    await sendMessage({
      message: currentMessage,
      agents: activeAgents,
      enableA2A: showA2APane,
      streaming: true,
    });
  };
  
  return (
    <div className="flex h-screen">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header with Agent Status */}
        <div className="border-b p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold">Multi-Agent Chat</h2>
              {activeAgents.length > 0 && (
                <Badge variant="secondary">
                  {activeAgents.length} agent{activeAgents.length !== 1 ? 's' : ''} active
                </Badge>
              )}
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowA2APane(!showA2APane)}
                className={cn(showA2APane && "bg-blue-50 border-blue-200")}
              >
                <Network className="w-4 h-4 mr-1" />
                A2A Messages
              </Button>
              <AgentSelectorDialog onAgentsChange={setActiveAgents} />
            </div>
          </div>
        </div>
        
        {/* Chat Messages */}
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <ChatMessageBubble
                key={message.id}
                message={message}
                showA2AContext={showA2APane}
              />
            ))}
          </div>
        </ScrollArea>
        
        {/* Message Input */}
        <div className="border-t p-4">
          <div className="flex gap-2">
            <Input
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              placeholder="Type your message..."
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              className="flex-1"
            />
            <Button onClick={handleSendMessage} disabled={!currentMessage.trim()}>
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
      
      {/* A2A Message Pane */}
      {showA2APane && (
        <div className="w-96 border-l bg-muted/30">
          <div className="p-4 border-b">
            <h3 className="font-semibold">A2A Communications</h3>
            <p className="text-sm text-muted-foreground">
              Real-time agent-to-agent messages
            </p>
          </div>
          
          <ScrollArea className="h-full p-4">
            <A2AMessageTimeline 
              messages={a2aMessages}
              activeAgents={activeAgents}
            />
          </ScrollArea>
        </div>
      )}
    </div>
  );
}
```

## 4. Advanced Visualization Components

### 4.1 Agent Network Visualization

```typescript
// components/visualization/agent-network-visualization.tsx
interface AgentNetworkVisualizationProps {
  coordinationState?: CoordinationContext;
  messages: A2AMessage[];
  interactive?: boolean;
}

export function AgentNetworkVisualization({
  coordinationState,
  messages,
  interactive = false
}: AgentNetworkVisualizationProps) {
  const [networkData, setNetworkData] = useState<NetworkData>();
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  
  // Transform coordination data into network visualization
  useEffect(() => {
    if (!coordinationState || !messages.length) return;
    
    const nodes = coordinationState.participants.map(participant => ({
      id: participant.agentId,
      label: participant.agentId,
      group: participant.role,
      status: participant.status,
      size: messages.filter(m => m.from === participant.agentId).length + 10,
      color: getAgentColor(participant.role),
    }));
    
    const edges = messages.map(message => ({
      id: message.id,
      from: message.from,
      to: message.to === '*' ? 'broadcast' : message.to,
      label: message.intent,
      color: getMessageTypeColor(message.type),
      width: message.payload.metadata.priority,
      arrows: 'to',
      smooth: { type: 'dynamic' },
    }));
    
    setNetworkData({ nodes, edges });
  }, [coordinationState, messages]);
  
  return (
    <div className="relative w-full h-96">
      {networkData && (
        <VisNetwork
          data={networkData}
          options={{
            physics: {
              enabled: true,
              stabilization: { iterations: 100 },
            },
            interaction: {
              selectConnectedEdges: false,
              hover: true,
            },
            nodes: {
              shape: 'dot',
              scaling: { min: 10, max: 30 },
              font: { size: 12, color: 'white' },
            },
            edges: {
              width: 2,
              color: { inherit: 'from' },
              smooth: { type: 'dynamic' },
            },
          }}
          events={{
            selectNode: (event) => {
              if (interactive && event.nodes.length > 0) {
                setSelectedAgent(event.nodes[0]);
              }
            },
          }}
        />
      )}
      
      {/* Agent Details Panel */}
      {selectedAgent && (
        <div className="absolute top-2 right-2 w-64 bg-white border rounded-lg shadow-lg p-3">
          <AgentDetailsPanel agentId={selectedAgent} />
        </div>
      )}
    </div>
  );
}
```

This comprehensive frontend specification provides the foundation for building a sophisticated Agentic AI Acceleration with full A2A protocol support, MCP integration, and real-time visualization capabilities.

### UI Component Library
```json
{
  "ui-components": {
    "@radix-ui/react-accordion": "^1.1.2",
    "@radix-ui/react-alert-dialog": "^1.0.5",
    "@radix-ui/react-avatar": "^1.0.4",
    "@radix-ui/react-checkbox": "^1.0.4",
    "@radix-ui/react-collapsible": "^1.0.3",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-hover-card": "^1.0.7",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-menubar": "^1.0.4",
    "@radix-ui/react-navigation-menu": "^1.1.4",
    "@radix-ui/react-popover": "^1.0.7",
    "@radix-ui/react-progress": "^1.0.3",
    "@radix-ui/react-radio-group": "^1.1.3",
    "@radix-ui/react-scroll-area": "^1.0.5",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-separator": "^1.0.3",
    "@radix-ui/react-sheet": "^1.0.5",
    "@radix-ui/react-slider": "^1.1.2",
    "@radix-ui/react-switch": "^1.0.3",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "@radix-ui/react-toggle": "^1.0.3",
    "@radix-ui/react-toggle-group": "^1.0.4",
    "@radix-ui/react-tooltip": "^1.0.7"
  }
}
```

### State Management & Data Fetching
```json
{
  "state-management": {
    "zustand": "^4.5.0",
    "@tanstack/react-query": "^5.28.0",
    "@tanstack/react-query-devtools": "^5.28.0",
    "axios": "^1.6.0",
    "swr": "^2.2.0"
  }
}
```

### Visualization & Charts
```json
{
  "visualization": {
    "recharts": "^2.12.0",
    "d3": "^7.9.0",
    "@types/d3": "^7.4.0",
    "mermaid": "^10.9.0",
    "reactflow": "^11.11.0",
    "@xyflow/react": "^12.0.0",
    "cytoscape": "^3.28.0",
    "cytoscape-react": "^2.0.0"
  }
}
```

### Form Handling & Validation
```json
{
  "forms": {
    "react-hook-form": "^7.51.0",
    "@hookform/resolvers": "^3.3.0",
    "zod": "^3.22.0",
    "react-dropzone": "^14.2.0"
  }
}
```

### Utilities & Helpers
```json
{
  "utilities": {
    "date-fns": "^3.6.0",
    "lodash": "^4.17.0",
    "@types/lodash": "^4.17.0",
    "uuid": "^9.0.0",
    "@types/uuid": "^9.0.0",
    "nanoid": "^5.0.0",
    "js-cookie": "^3.0.0",
    "@types/js-cookie": "^3.0.0"
  }
}
```

## 2. Project Structure

```
apps/web/
├── public/
│   ├── icons/
│   ├── images/
│   └── favicon.ico
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── loading.tsx
│   │   ├── error.tsx
│   │   ├── not-found.tsx
│   │   ├── (auth)/                   # Auth group
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── dashboard/                # Dashboard pages
│   │   │   ├── page.tsx
│   │   │   └── loading.tsx
│   │   ├── agents/                   # Agent management
│   │   │   ├── page.tsx
│   │   │   ├── [id]/
│   │   │   ├── create/
│   │   │   └── templates/
│   │   ├── workflows/                # Workflow management
│   │   │   ├── page.tsx
│   │   │   ├── [id]/
│   │   │   ├── create/
│   │   │   └── designer/
│   │   ├── tools/                    # Tool management
│   │   │   ├── page.tsx
│   │   │   ├── [id]/
│   │   │   ├── mcp/
│   │   │   └── sql/
│   │   ├── rag/                      # RAG management
│   │   │   ├── page.tsx
│   │   │   ├── documents/
│   │   │   └── indexes/
│   │   ├── chat/                     # Chat interface
│   │   │   ├── page.tsx
│   │   │   └── [sessionId]/
│   │   ├── observability/            # Monitoring
│   │   │   ├── page.tsx
│   │   │   ├── traces/
│   │   │   ├── metrics/
│   │   │   └── logs/
│   │   ├── api-management/           # API management
│   │   │   ├── page.tsx
│   │   │   ├── endpoints/
│   │   │   └── pipelines/
│   │   └── api/                      # API routes
│   │       ├── auth/
│   │       ├── upload/
│   │       └── proxy/
│   ├── components/                   # Reusable components
│   │   ├── ui/                       # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── form.tsx
│   │   │   ├── input.tsx
│   │   │   ├── select.tsx
│   │   │   ├── table.tsx
│   │   │   ├── tabs.tsx
│   │   │   └── toast.tsx
│   │   ├── layout/                   # Layout components
│   │   │   ├── header.tsx
│   │   │   ├── sidebar.tsx
│   │   │   ├── navbar.tsx
│   │   │   └── footer.tsx
│   │   ├── agents/                   # Agent components
│   │   │   ├── agent-card.tsx
│   │   │   ├── agent-form.tsx
│   │   │   ├── agent-list.tsx
│   │   │   ├── skill-selector.tsx
│   │   │   └── agent-tester.tsx
│   │   ├── workflows/                # Workflow components
│   │   │   ├── workflow-designer.tsx
│   │   │   ├── workflow-card.tsx
│   │   │   ├── workflow-form.tsx
│   │   │   ├── node-palette.tsx
│   │   │   └── flow-canvas.tsx
│   │   ├── tools/                    # Tool components
│   │   │   ├── tool-card.tsx
│   │   │   ├── tool-form.tsx
│   │   │   ├── mcp-browser.tsx
│   │   │   ├── sql-editor.tsx
│   │   │   └── tool-tester.tsx
│   │   ├── rag/                      # RAG components
│   │   │   ├── document-uploader.tsx
│   │   │   ├── document-viewer.tsx
│   │   │   ├── index-manager.tsx
│   │   │   └── search-interface.tsx
│   │   ├── chat/                     # Chat components
│   │   │   ├── chat-interface.tsx
│   │   │   ├── message-bubble.tsx
│   │   │   ├── input-panel.tsx
│   │   │   ├── scratch-pad.tsx
│   │   │   ├── citation-viewer.tsx
│   │   │   └── file-uploader.tsx
│   │   ├── observability/            # Monitoring components
│   │   │   ├── trace-viewer.tsx
│   │   │   ├── metrics-dashboard.tsx
│   │   │   ├── log-viewer.tsx
│   │   │   ├── performance-chart.tsx
│   │   │   └── event-timeline.tsx
│   │   ├── charts/                   # Chart components
│   │   │   ├── area-chart.tsx
│   │   │   ├── bar-chart.tsx
│   │   │   ├── line-chart.tsx
│   │   │   ├── pie-chart.tsx
│   │   │   └── network-graph.tsx
│   │   ├── forms/                    # Form components
│   │   │   ├── form-field.tsx
│   │   │   ├── file-upload.tsx
│   │   │   ├── code-editor.tsx
│   │   │   ├── json-editor.tsx
│   │   │   └── multi-select.tsx
│   │   └── common/                   # Common components
│   │       ├── loading-spinner.tsx
│   │       ├── error-boundary.tsx
│   │       ├── confirmation-dialog.tsx
│   │       ├── data-table.tsx
│   │       └── search-bar.tsx
│   ├── hooks/                        # Custom hooks
│   │   ├── use-auth.ts
│   │   ├── use-api.ts
│   │   ├── use-websocket.ts
│   │   ├── use-local-storage.ts
│   │   ├── use-debounce.ts
│   │   ├── use-agents.ts
│   │   ├── use-workflows.ts
│   │   ├── use-tools.ts
│   │   └── use-observability.ts
│   ├── lib/                          # Utility libraries
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   ├── utils.ts
│   │   ├── constants.ts
│   │   ├── validations.ts
│   │   ├── websocket.ts
│   │   └── storage.ts
│   ├── store/                        # State management
│   │   ├── auth-store.ts
│   │   ├── agent-store.ts
│   │   ├── workflow-store.ts
│   │   ├── tool-store.ts
│   │   ├── chat-store.ts
│   │   └── observability-store.ts
│   ├── types/                        # TypeScript types
│   │   ├── api.ts
│   │   ├── agent.ts
│   │   ├── workflow.ts
│   │   ├── tool.ts
│   │   ├── chat.ts
│   │   ├── observability.ts
│   │   └── common.ts
│   └── styles/                       # Global styles
│       ├── globals.css
│       ├── components.css
│       └── utilities.css
├── tests/                            # Tests
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   └── e2e/
├── next.config.mjs
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

## 3. Core Type Definitions

### 3.1 Agent Types
```typescript
// types/agent.ts
export interface Agent {
  id: string;
  name: string;
  description: string;
  framework: 'langchain' | 'llamaindex' | 'crewai' | 'semantic-kernel';
  skills: string[];
  config: AgentConfig;
  status: 'active' | 'inactive' | 'error';
  createdAt: Date;
  updatedAt: Date;
}

export interface AgentConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  systemPrompt: string;
  tools: string[];
  memory: boolean;
  streaming: boolean;
  [key: string]: any;
}

export interface AgentTemplate {
  id: string;
  name: string;
  description: string;
  framework: string;
  defaultConfig: AgentConfig;
  skills: string[];
  category: string;
}

export interface AgentExecution {
  id: string;
  agentId: string;
  input: any;
  output: any;
  status: 'running' | 'completed' | 'failed';
  startTime: Date;
  endTime?: Date;
  duration?: number;
  traceId: string;
}
```

### 3.2 Workflow Types
```typescript
// types/workflow.ts
export interface Workflow {
  id: string;
  name: string;
  description: string;
  definition: WorkflowDefinition;
  status: 'draft' | 'active' | 'inactive';
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface WorkflowDefinition {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  variables: WorkflowVariable[];
  triggers: WorkflowTrigger[];
}

export interface WorkflowNode {
  id: string;
  type: 'agent' | 'tool' | 'condition' | 'parallel' | 'merge';
  position: { x: number; y: number };
  data: {
    label: string;
    agentId?: string;
    toolId?: string;
    config?: any;
  };
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  type: 'default' | 'conditional';
  condition?: string;
}

export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: 'running' | 'completed' | 'failed' | 'paused';
  input: any;
  output?: any;
  currentNode?: string;
  startTime: Date;
  endTime?: Date;
  traceId: string;
}
```

### 3.3 Tool Types
```typescript
// types/tool.ts
export interface Tool {
  id: string;
  name: string;
  description: string;
  type: 'mcp' | 'sql' | 'rag' | 'standard';
  config: ToolConfig;
  parameters: ToolParameter[];
  status: 'active' | 'inactive' | 'error';
  createdAt: Date;
}

export interface ToolConfig {
  serverUrl?: string;
  apiKey?: string;
  connectionString?: string;
  database?: string;
  indexName?: string;
  [key: string]: any;
}

export interface ToolParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  required: boolean;
  description: string;
  default?: any;
  enum?: string[];
}

export interface MCPTool extends Tool {
  serverId: string;
  serverUrl: string;
  capabilities: string[];
  methods: MCPMethod[];
}

export interface MCPMethod {
  name: string;
  description: string;
  parameters: ToolParameter[];
  returns: any;
}
```

### 3.4 Chat Types
```typescript
// types/chat.ts
export interface ChatSession {
  id: string;
  workflowId?: string;
  messages: ChatMessage[];
  metadata: ChatMetadata;
  status: 'active' | 'completed';
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'agent' | 'system';
  content: string;
  type: 'text' | 'image' | 'file' | 'mermaid';
  metadata?: {
    agentId?: string;
    toolId?: string;
    citations?: Citation[];
    attachments?: Attachment[];
  };
  timestamp: Date;
}

export interface Citation {
  id: string;
  source: string;
  title: string;
  url?: string;
  excerpt: string;
  confidence: number;
}

export interface Attachment {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
}

export interface ChatMetadata {
  workflowName?: string;
  agentIds: string[];
  toolIds: string[];
  totalMessages: number;
  totalTokens: number;
}
```

### 3.5 Observability Types
```typescript
// types/observability.ts
export interface Trace {
  id: string;
  traceId: string;
  operationName: string;
  serviceName: string;
  startTime: Date;
  endTime: Date;
  duration: number;
  status: 'ok' | 'error' | 'timeout';
  spans: Span[];
  tags: Record<string, any>;
}

export interface Span {
  id: string;
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  operationName: string;
  serviceName: string;
  startTime: Date;
  endTime: Date;
  duration: number;
  status: 'ok' | 'error';
  tags: Record<string, any>;
  logs: LogEntry[];
}

export interface LogEntry {
  timestamp: Date;
  level: 'debug' | 'info' | 'warn' | 'error';
  message: string;
  fields: Record<string, any>;
}

export interface Metric {
  name: string;
  type: 'counter' | 'gauge' | 'histogram';
  value: number;
  labels: Record<string, string>;
  timestamp: Date;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  services: ServiceHealth[];
  uptime: number;
  lastCheck: Date;
}

export interface ServiceHealth {
  name: string;
  status: 'healthy' | 'unhealthy';
  responseTime: number;
  errorRate: number;
  lastCheck: Date;
}
```

## 4. State Management Architecture

### 4.1 Zustand Store Structure
```typescript
// store/agent-store.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface AgentState {
  agents: Agent[];
  selectedAgent: Agent | null;
  templates: AgentTemplate[];
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setAgents: (agents: Agent[]) => void;
  addAgent: (agent: Agent) => void;
  updateAgent: (id: string, updates: Partial<Agent>) => void;
  deleteAgent: (id: string) => void;
  selectAgent: (agent: Agent | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAgentStore = create<AgentState>()(
  devtools(
    (set, get) => ({
      agents: [],
      selectedAgent: null,
      templates: [],
      isLoading: false,
      error: null,
      
      setAgents: (agents) => set({ agents }),
      addAgent: (agent) => set((state) => ({ 
        agents: [...state.agents, agent] 
      })),
      updateAgent: (id, updates) => set((state) => ({
        agents: state.agents.map((agent) =>
          agent.id === id ? { ...agent, ...updates } : agent
        )
      })),
      deleteAgent: (id) => set((state) => ({
        agents: state.agents.filter((agent) => agent.id !== id)
      })),
      selectAgent: (agent) => set({ selectedAgent: agent }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error })
    }),
    { name: 'agent-store' }
  )
);
```

### 4.2 React Query Integration
```typescript
// hooks/use-agents.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { agentApi } from '@/lib/api';
import { useAgentStore } from '@/store/agent-store';

export function useAgents() {
  const { setAgents, setLoading, setError } = useAgentStore();
  
  return useQuery({
    queryKey: ['agents'],
    queryFn: agentApi.getAll,
    onSuccess: (data) => {
      setAgents(data);
      setLoading(false);
    },
    onError: (error) => {
      setError(error.message);
      setLoading(false);
    },
    onLoading: () => setLoading(true)
  });
}

export function useCreateAgent() {
  const queryClient = useQueryClient();
  const { addAgent } = useAgentStore();
  
  return useMutation({
    mutationFn: agentApi.create,
    onSuccess: (newAgent) => {
      addAgent(newAgent);
      queryClient.invalidateQueries(['agents']);
    }
  });
}
```

## 5. API Integration Layer

### 5.1 API Client Configuration
```typescript
// lib/api.ts
import axios, { AxiosResponse } from 'axios';
import { getAuthToken, clearAuthToken } from './auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:3000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearAuthToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Generic API methods
class ApiService<T> {
  constructor(private endpoint: string) {}
  
  async getAll(): Promise<T[]> {
    const response = await apiClient.get<T[]>(this.endpoint);
    return response.data;
  }
  
  async getById(id: string): Promise<T> {
    const response = await apiClient.get<T>(`${this.endpoint}/${id}`);
    return response.data;
  }
  
  async create(data: Omit<T, 'id'>): Promise<T> {
    const response = await apiClient.post<T>(this.endpoint, data);
    return response.data;
  }
  
  async update(id: string, data: Partial<T>): Promise<T> {
    const response = await apiClient.put<T>(`${this.endpoint}/${id}`, data);
    return response.data;
  }
  
  async delete(id: string): Promise<void> {
    await apiClient.delete(`${this.endpoint}/${id}`);
  }
}

// Service instances
export const agentApi = new ApiService<Agent>('/agents');
export const workflowApi = new ApiService<Workflow>('/workflows');
export const toolApi = new ApiService<Tool>('/tools');
export const chatApi = new ApiService<ChatSession>('/chat');
```

### 5.2 WebSocket Integration
```typescript
// lib/websocket.ts
import { useEffect, useRef, useState } from 'react';

interface UseWebSocketOptions {
  onMessage?: (data: any) => void;
  onError?: (error: Event) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttempts = useRef(0);
  
  const connect = () => {
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;
      
      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
        options.onConnect?.();
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          options.onMessage?.(data);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };
      
      ws.onerror = (error) => {
        setError('WebSocket connection error');
        options.onError?.(error);
      };
      
      ws.onclose = () => {
        setIsConnected(false);
        options.onDisconnect?.();
        
        // Attempt reconnection
        if (reconnectAttempts.current < (options.reconnectAttempts || 5)) {
          reconnectAttempts.current++;
          reconnectTimeoutRef.current = setTimeout(
            connect,
            options.reconnectDelay || 3000
          );
        }
      };
    } catch (e) {
      setError('Failed to create WebSocket connection');
    }
  };
  
  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    wsRef.current?.close();
  };
  
  const sendMessage = (data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  };
  
  useEffect(() => {
    connect();
    return disconnect;
  }, [url]);
  
  return {
    isConnected,
    error,
    sendMessage,
    disconnect
  };
}
```

## 6. Component Examples

### 6.1 Agent Management Component
```typescript
// components/agents/agent-list.tsx
'use client';

import { useState } from 'react';
import { Plus, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { AgentCard } from './agent-card';
import { AgentForm } from './agent-form';
import { useAgents } from '@/hooks/use-agents';
import { Agent } from '@/types/agent';

export function AgentList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFramework, setSelectedFramework] = useState('all');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  
  const { data: agents, isLoading, error } = useAgents();
  
  const filteredAgents = agents?.filter((agent: Agent) => {
    const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFramework = selectedFramework === 'all' || agent.framework === selectedFramework;
    return matchesSearch && matchesFramework;
  });
  
  if (isLoading) {
    return <div className="flex items-center justify-center h-64">Loading agents...</div>;
  }
  
  if (error) {
    return <div className="text-red-500">Error loading agents: {error.message}</div>;
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Agents</h1>
          <p className="text-muted-foreground">Manage your AI agents and their configurations</p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Agent
        </Button>
      </div>
      
      {/* Filters */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search agents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={selectedFramework} onValueChange={setSelectedFramework}>
          <SelectTrigger className="w-48">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue placeholder="Filter by framework" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Frameworks</SelectItem>
            <SelectItem value="langchain">LangChain</SelectItem>
            <SelectItem value="llamaindex">LlamaIndex</SelectItem>
            <SelectItem value="crewai">CrewAI</SelectItem>
            <SelectItem value="semantic-kernel">Semantic Kernel</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAgents?.map((agent: Agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
      
      {/* Create Modal */}
      <AgentForm
        open={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
}
```

### 6.2 Workflow Designer Component
```typescript
// components/workflows/workflow-designer.tsx
'use client';

import { useCallback, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { AgentNode } from './nodes/agent-node';
import { ToolNode } from './nodes/tool-node';
import { ConditionNode } from './nodes/condition-node';
import { NodePalette } from './node-palette';
import { WorkflowDefinition } from '@/types/workflow';

const nodeTypes = {
  agent: AgentNode,
  tool: ToolNode,
  condition: ConditionNode,
};

interface WorkflowDesignerProps {
  initialDefinition?: WorkflowDefinition;
  onDefinitionChange?: (definition: WorkflowDefinition) => void;
}

export function WorkflowDesigner({ 
  initialDefinition, 
  onDefinitionChange 
}: WorkflowDesignerProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(
    initialDefinition?.nodes || []
  );
  const [edges, setEdges, onEdgesChange] = useEdgesState(
    initialDefinition?.edges || []
  );
  
  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );
  
  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      
      const reactFlowBounds = event.currentTarget.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/reactflow');
      
      if (!type) return;
      
      const position = {
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      };
      
      const newNode: Node = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: { label: `${type} node` },
      };
      
      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes]
  );
  
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);
  
  // Update parent component when definition changes
  useEffect(() => {
    if (onDefinitionChange) {
      onDefinitionChange({
        nodes,
        edges,
        variables: [],
        triggers: [],
      });
    }
  }, [nodes, edges, onDefinitionChange]);
  
  return (
    <div className="flex h-screen">
      {/* Node Palette */}
      <div className="w-64 border-r bg-muted/50">
        <NodePalette />
      </div>
      
      {/* Flow Canvas */}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDrop={onDrop}
          onDragOver={onDragOver}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <MiniMap />
          <Background variant="dots" gap={12} size={1} />
        </ReactFlow>
      </div>
    </div>
  );
}
```

This comprehensive frontend specification provides a solid foundation for building the Agentic AI Acceleration frontend. Each team can use these specifications with GitHub Copilot to implement their respective components efficiently.
