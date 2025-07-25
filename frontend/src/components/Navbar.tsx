'use client';

import Link from 'next/link';
import { useAccount, useConnect, useDisconnect, useChainId, useSwitchChain } from 'wagmi';
import { metaMask } from '@wagmi/connectors';

export default function Navbar() {
  const { address, isConnected, chain } = useAccount();
  const { connect, isPending: isConnectPending } = useConnect();
  const { disconnect } = useDisconnect();
  const chainId = useChainId();
  const { switchChain } = useSwitchChain();

  const connectWallet = () => {
    connect({ connector: metaMask() });
  };

  const disconnectWallet = () => {
    disconnect();
  };

  const formatAddress = (address: string) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  // Switch to Metis if not already connected
  const switchToMetis = () => {
    if (switchChain) {
      switchChain({ chainId: 1088 }); // Metis Mainnet
    }
  };

  const getChainName = (chainId: number) => {
    switch (chainId) {
      case 1088:
        return 'Metis';
      case 588:
        return 'Metis Testnet';
      case 1:
        return 'Ethereum';
      case 11155111:
        return 'Sepolia';
      default:
        return 'Unknown';
    }
  };

  const isWrongNetwork = chainId !== 1088 && chainId !== 588; // Not Metis networks

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Left side - TokenLab brand */}
          <div className="flex items-center">
            <Link href="/" className="text-2xl font-bold text-blue-600 hover:text-blue-700 transition-colors">
              TokenLab
            </Link>
          </div>

          {/* Right side - Connect button and Create Service button */}
          <div className="flex items-center space-x-4">
            {/* Create New Service Button */}
            <Link
              href="/add-new-service"
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Create Service
            </Link>

            {/* Wallet Connection */}
            {!isConnected ? (
              <button
                onClick={connectWallet}
                disabled={isConnectPending}
                className="bg-orange-500 hover:bg-orange-600 disabled:bg-orange-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-2"
              >
                <svg
                  className="w-4 h-4"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span>{isConnectPending ? 'Connecting...' : 'Connect Wallet'}</span>
              </button>
            ) : (
              <div className="flex items-center space-x-2">
                {/* Network Indicator */}
                <div className="flex items-center space-x-2">
                  <div 
                    className={`w-2 h-2 rounded-full ${
                      isWrongNetwork ? 'bg-red-500' : 'bg-green-500'
                    }`}
                  />
                  <span className="text-sm text-gray-600">
                    {getChainName(chainId)}
                  </span>
                  {isWrongNetwork && (
                    <button
                      onClick={switchToMetis}
                      className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded hover:bg-red-200 transition-colors"
                    >
                      Switch to Metis
                    </button>
                  )}
                </div>

                {/* Connected Address */}
                <div className="bg-green-100 text-green-800 px-3 py-1 rounded-md text-sm font-medium">
                  {formatAddress(address || '')}
                </div>

                {/* Disconnect Button */}
                <button
                  onClick={disconnectWallet}
                  className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-md text-sm font-medium transition-colors"
                >
                  Disconnect
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
