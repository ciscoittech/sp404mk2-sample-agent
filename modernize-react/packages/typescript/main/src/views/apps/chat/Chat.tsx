// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useState } from 'react';
import { Divider, Box } from '@mui/material';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ChatSidebar from 'src/components/apps/chats/ChatSidebar';
import ChatContent from 'src/components/apps/chats/ChatContent';
import ChatMsgSent from 'src/components/apps/chats/ChatMsgSent';
import AppCard from 'src/components/shared/AppCard';
import { ChatProvider } from 'src/context/ChatContext';

const Chats = () => {
  const [isMobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const BCrumb = [
    {
      to: '/',
      title: 'Home',
    },
    {
      title: 'Chat',
    },
  ];
  return (
    <ChatProvider>
      <PageContainer title="Chat ui" description="this is Chat page">
        <Breadcrumb title="Chat app" items={BCrumb} />
        <AppCard>
          {/* ------------------------------------------- */}
          {/* Left part */}
          {/* ------------------------------------------- */}

          <ChatSidebar
            isMobileSidebarOpen={isMobileSidebarOpen}
            onSidebarClose={() => setMobileSidebarOpen(false)}
          />
          {/* ------------------------------------------- */}
          {/* Right part */}
          {/* ------------------------------------------- */}

          <Box flexGrow={1}>
            <ChatContent toggleChatSidebar={() => setMobileSidebarOpen(true)} />
            <Divider />
            <ChatMsgSent />
          </Box>
        </AppCard>
      </PageContainer>
    </ChatProvider>
  );
};

export default Chats;
