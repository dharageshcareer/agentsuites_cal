document.addEventListener('DOMContentLoaded', () => {
    const agentListContainer = document.getElementById('agent-list');
    const loginForm = document.getElementById('login-form');

    // --- Agent Listing Logic (for index.html) ---
    if (agentListContainer) {
        // Define the endpoint for fetching the list of agents
        const AGENTS_API_URL = 'http://127.0.0.1:8000/api/agents';

        const fetchAndRenderAgents = async () => {
            const loadingState = document.getElementById('loading-state');
            try {
                const response = await fetch(AGENTS_API_URL);
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                const agents = await response.json();

                // Clear the loading indicator
                agentListContainer.innerHTML = '';

                if (agents.length === 0) {
                    agentListContainer.innerHTML = '<p class="col-span-full text-center text-gray-500">No agents are available at the moment.</p>';
                    return;
                }

                // Render each agent card
                agents.forEach(agent => {
                    const agentCard = createAgentCard(agent);
                    agentListContainer.insertAdjacentHTML('beforeend', agentCard);
                });

            } catch (error) {
                console.error('Failed to fetch agents:', error);
                if (loadingState) {
                    loadingState.textContent = 'Failed to load agents. Please check the connection and try again.';
                    loadingState.classList.add('text-red-500');
                }
            }
        };

        const createAgentCard = (agent) => {
            // Use the provided SVG or a default one
            const iconSvg = agent.icon_svg || `
                <svg class="h-8 w-8 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
                </svg>`;

            // Determine the correct link for the agent.
            // This provides a client-side override to ensure specific agents work as expected
            // while migrating to a fully dynamic backend.
            let agentLink = agent.link; // Start with the link from the backend, if it exists.
            let isLinkActive = true;

            if (agent.agent_name === 'Instructor Assistant') {
                agentLink = 'instructor_assistant/instructor_assistant.html';
            } else if (agent.agent_name === 'Job Placement RAG') {
                agentLink = 'jobplacement/jobplacement_chat.html';
            }

            // Fallback to prevent 'undefined' in the URL and disable the link
            if (!agentLink) {
                isLinkActive = false;
                agentLink = '#'; // Use a safe, non-navigating link
                console.warn(
                    `Agent "${agent.agent_name || 'Unknown Agent'}" is missing a 'link' property from the backend and has no frontend override. The link has been disabled.`
                );
            }

            return `
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                ${iconSvg}
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">
                                        ${agent.agent_name || 'Unnamed Agent'}
                                    </dt>
                                    <dd>
                                        <div class="text-lg font-medium text-gray-900">${agent.description || ''}</div>
                                    </dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                    <div class="bg-gray-50 px-5 py-3">
                        <div class="text-sm">
                            <a href="${agentLink}" class="${isLinkActive 
                                ? 'font-medium brand-text brand-text-hover' 
                                : 'font-medium text-gray-400 cursor-not-allowed'}" 
                                ${!isLinkActive ? 'onclick="return false;"' : ''}
                            > ${isLinkActive ? 'Go to agent &rarr;' : 'Not available'} </a>
                        </div>
                    </div>
                </div>
            `;
        };

        fetchAndRenderAgents();
    }

    // --- Login/Logout logic would go here ---
});