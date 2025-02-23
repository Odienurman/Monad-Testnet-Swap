o
    ��g�  �                   @   s�  d dl Z d dlZd dlmZ d dlZd dlmZmZmZ edd� e�	d�Z
eejej e
 � eejej d � eejej d � d	Zee�e��Ze�� s[eejd
 � e�  ejjZeejde� � � e�d�Zd"dd�Zdd� Zdd� Zdd� Zdd� Zedkr�e e!d��Z"e"d kr�eejd � e�  e#e!d��Z$e$d kr�eejd � e�  e e!d��Z%e%d kr�eejd � e�  e� Z&e&s�eejd � e�  ed � ee&e"e$e%� eejd! � dS dS )#�    N)�Web3)�Fore�Style�initT)Z	autoresetz	Si GUNDULz'Auto Swap MON to WMON and Auto Withdrawz)BOT Created By https://t.me/sigundulmaniazhttps://testnet-rpc.monad.xyz/u?   ❌ Gagal terhubung ke Monad Testnet RPC! Periksa koneksi Anda.u*   ✅ Terhubung ke Monad Testnet! Chain ID: Z*0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701�
   c           	   
   C   s  d}||k rz3t j�| d d�}|| d< t j�| �| d< t jj�| |�}t j�|j�}tt	j
d|�� � � � |W S  tyz } z5dt|�v rYtt	jd � t�d	� W Y d }~qtt	jd
|� d|� d� � t�|� |d7 }W Y d }~nd }~ww ||k stt	jd � d S )Nr   �from�pending�nonceZgasu!   ✅ Transaksi berhasil! TX Hash: znonce too lowu,   ⚠️ Nonce terlalu rendah, mencoba lagi...�   u!   ⚠️ Gagal mengirim transaksi: z. Mencoba ulang dalam z	 detik...�   u=   ❌ Gagal mengirim transaksi setelah beberapa kali percobaan.)�web3�eth�get_transaction_countZestimate_gas�accountZsign_transactionZsend_raw_transactionZrawTransaction�printr   �GREEN�hex�	Exception�strZYELLOW�time�sleep�MAGENTA�RED)	ZtransactionZprivate_keyZmax_retriesZdelayZretriesr	   Z
signed_txnZtx_hash�e� r   �
monswap.py�send_transaction_with_retry    s.   

���r   c              
   C   s�   zJt �|d�}t jdd�d d� }t�| j�t|t �|d�t j�| jd�t	|�
� d�}t|| j� ttjd| j� d	� � t�d
� t| ||� W d S  tyk } zttjd| j� d|� � � W Y d }~d S d }~ww )NZetherz	deposit()��text�   �gweir   )r   �to�value�gasPricer	   �chainId�data�   ✅ [z] Berhasil deposit MON ke WMONr
   �   
❌ [z] Gagal deposit MON ke WMON: )r   �to_wei�keccakr   �to_checksum_address�address�WMONr   r   �CHAIN_IDr   r   �keyr   r   r   r   r   �withdraw_wmon_to_monr   r   )�walletZamount_in_mon�	gas_price�amount_in_weiZdeposit_function_selector�txn�errorr   r   r   �deposit_mon_to_wmon6   s&   

�

*��r5   c              
   C   s�   zNt |�}tjdd�d d� }|�dd�}|| }t�| j�tt�|d�tj	�
| jd�t|�� d�}t|| j� ttjd	| j� d
|� d� � t�d� W d S  tyo } zttjd| j� d|� � � W Y d }~d S d }~ww )Nzwithdraw(uint256)r   r   �    Zbigr    r   )r   r!   r#   r	   r$   r%   r&   z)] Berhasil withdraw WMON ke MON sebanyak z Weir
   r'   z] Gagal withdraw WMON ke MON: )�intr   r)   �to_bytesr   r*   r+   r,   r(   r   r   r-   r   r   r.   r   r   r   r   r   r   r   )r0   r2   r1   Zwithdraw_function_selectorZamount_paddedr%   r3   r4   r   r   r   r/   L   s&   

�	*��r/   c              	   C   sX   | D ]'}t d|j� �� t|�D ]}t d|d � d|� d|j� �� t|||� qqd S )Nu&   
🚀 Memulai transaksi untuk wallet: u   
🔄 Transaksi r   z dari z untuk )r   r+   �ranger5   )�wallets�amountZtransactions_per_walletr1   r0   �ir   r   r   �process_walletsb   s    ��r=   c                  C   sJ   t dd��} dd� | �� D �}W d   � n1 sw   Y  dd� |D �S )Nz
pvkeys.txt�rc                 S   s   g | ]
}|� � r|� � �qS r   )�strip)�.0�liner   r   r   �
<listcomp>k   s    z load_wallets.<locals>.<listcomp>c                 S   s   g | ]	}t jj�|��qS r   )r   r   r   Zfrom_key)r@   Zpkr   r   r   rB   l   s    )�open�	readlines)�fileZprivate_keysr   r   r   �load_walletsi   s   �rF   �__main__u9   
💱 Masukkan jumlah MON yang ingin di-deposit ke WMON: u#   
⚠️ Masukkan jumlah yang valid!u,   
🔁 Masukkan jumlah transaksi per wallet: u-   
⚠️ Masukkan jumlah transaksi yang valid!u    
⛽ Masukkan gas price (Gwei): u&   
⚠️ Masukkan gas price yang valid!u.   
❌ Tidak ada wallet ditemukan di pvkeys.txt!u%   
📋 Memulai deposit dan withdraw...u   
🎉 Semua transaksi selesai!)r   r   )'Zjsonr   r   r   ZpyfigletZcoloramar   r   r   Zfiglet_formatZbannerr   r   ZBRIGHTZCYANZRPC_URLZHTTPProviderZis_connectedr   �exitr   Zchain_idr-   r   r*   r,   r   r5   r/   r=   rF   �__name__�float�inputr;   r7   Ztransactionsr1   r:   r   r   r   r   �<module>   sX    



�